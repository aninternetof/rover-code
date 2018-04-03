"""Rovercode app."""
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests, json, socket
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv, find_dotenv
import os
try:
    import Adafruit_GPIO.PWM as pwmLib
    import Adafruit_GPIO.GPIO as gpioLib
except ImportError:
    print "Adafruit_GPIO lib unavailable"

"""Globals"""
ROVERCODE_WEB_REG_URL = ''
ROVERCODE_WEB_OAUTH2_URL = ''
DEFAULT_SOFTPWM_FREQ = 100
binary_sensors = []
ws_thread = None
hb_thread = None

try:
    pwm = pwmLib.get_platform_pwm(pwmtype="softpwm")
    gpio = gpioLib.get_platform_gpio()
except NameError:
    print "Adafruit_GPIO lib is unavailable"

"""Create flask app"""
app = Flask(__name__)
CORS(app, resources={r'/api/*': {"origins": [".*rovercode.com", ".*localhost"]}})
socketio = SocketIO(app )

class BinarySensor:
    """
    The binary sensor object contains information for each binary sensor.

    :param name:
        The human readable name of the sensor
    :param pin:
        The hardware pin connected to the sensor
    :param rising_event:
        The event name associated with a signal changing from low to high
    :param falling_event:
        The event name associated with a signal changing from high to low
    """

    def __init__(self, name, pin, rising_event, falling_event):
        """Constructor for BinarySensor object."""
        self.name = name
        self.pin = pin
        self.rising_event = rising_event
        self.falling_event = falling_event
        self.old_val = False

def get_local_ip():
    """Get the local area network IP address of the rover."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

class HeartBeatManager():
    """
    A manager to register the rover with rovercode-web and periodically check in.

    :param client_id:
        The Oauth2 client id for this rover.
    :param client_secret:
        The Oauth2 client secret for this rover.
    """

    def __init__(self, client_id, client_secret, id=None):
        """Constructor for the HeartBeatManager."""
        self.run = True
        self.thread = None
        self.web_id = id
        self.client_id = client_id
        self.name = None
        self.local_ip = get_local_ip()
        self.auth_header = None

        # Log in to rovercode-web using oauth credentials
        login_data = {
            'grant_type':'client_credentials',
            'client_id':client_id,
            'client_secret':client_secret,
        }
        r = requests.post(ROVERCODE_WEB_OAUTH2_URL + '/', data=login_data)
        self.auth_header = {'Authorization':'Bearer '+r.json()['access_token']}

    def update(self):
        """Check in with rovercode-web, updating our timestamp."""
        payload = {'name': self.name, 'local_ip': self.local_ip}
        return requests.put(ROVERCODE_WEB_REG_URL+"/"+str(self.web_id)+"/",
                                data=payload,
                                headers=self.auth_header)

    def read(self):
        """Look for our name on rovercode-web. Sets web_id if found."""
        result = requests.get(ROVERCODE_WEB_REG_URL+'?oauth_application__client_id='+self.client_id, headers=self.auth_header)
        try:
            info = json.loads(result.text)[0]
            self.web_id = info['id']
            self.name = info['name']
            init_input_gpio(info['left_eye_pin'], info['right_eye_pin'])
        except (KeyError, IndexError):
            self.web_id = None

    def stopThread(self):
        """Gracefully stop the periodic check-in thread."""
        self.run = False

    def thread_func(self, run_once=False):
        """Thread function that periodically checks in with rovercode-web."""
        self.read()
        while self.run:
            if self.web_id is not None:
                print "Checking in with rovercode-web with ID " + str(self.web_id)
                r = self.update()
                if r.status_code in [200, 201]:
                    print "... success"
                else:
                    print "... error while updating"
            else:
                print "No rover web-id found when trying to update!"
            if run_once:
                break
            socketio.sleep(3)
        print "Exiting heartbeat thread"
        return


def sensors_thread():
    """Scan each binary sensor and sends events based on changes."""
    while True:
        global binary_sensors
        socketio.sleep(0.2)
        for s in binary_sensors:
            new_val = gpio.is_high(s.pin)
            if (s.old_val == False) and (new_val == True):
                print s.rising_event
                socketio.emit('binary_sensors', {'data': s.rising_event},
                    namespace='/api/v1')
            elif (s.old_val == True) and (new_val == False):
                print s.falling_event
                socketio.emit('binary_sensors', {'data': s.falling_event},
                    namespace='/api/v1')
            else:
                pass
            s.old_val = new_val

@socketio.on('connect', namespace='/api/v1')
def connect():
    """Connect to the rovercode-web websocket."""
    global ws_thread
    print 'Websocket connected'
    if ws_thread is None:
        ws_thread = socketio.start_background_task(target=sensors_thread)
    emit('status', {'data': 'Connected'})

@socketio.on('status', namespace='/api/v1')
def test_message(message):
    """Send a debug test message when status is received from rovercode-web."""
    print "Got a status message: " + message['data']

@app.route('/', methods = ['GET'])
def display_home_message():
    """Display a message if someone points a browser at the root."""
    return ("The rover is running its service at this address.")

@app.route('/api/v1/sendcommand', methods = ['POST'])
def send_command():
    """
    API: /sendcommand [POST].

    Executes the posted command

    **Available Commands:**::
        START_MOTOR
        STOP_MOTOR
    """
    run_command(request.form)
    return jsonify(request.form)

def init_input_gpio(left_eye_pin, right_eye_pin):
    """Initialize input GPIO."""
    global gpio
    try:
        # set up IR sensor gpio
        gpio.setup(right_eye_pin, gpioLib.IN)
        gpio.setup(left_eye_pin, gpioLib.IN)
    except NameError:
        print "Adafruit_GPIO lib is unavailable"
    global binary_sensors
    binary_sensors.append(BinarySensor("left_ir_sensor", left_eye_pin, 'leftEyeUncovered', 'leftEyeCovered'))
    binary_sensors.append(BinarySensor("right_ir_sensor", right_eye_pin, 'rightEyeUncovered', 'rightEyeCovered'))

    # test adapter
    if pwm.__class__.__name__ == 'DUMMY_PWM_Adapter':
        def mock_set_duty_cycle(pin, speed):
            print "Setting pin " + pin + " to speed " + str(speed)
        pwm.set_duty_cycle = mock_set_duty_cycle

def singleton(class_):
    """Helper class for creating a singleton."""
    instances = {}
    def getInstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        else:
            print "Warning: tried to create multiple instances of singleton " + class_.__name__
        return instances[class_]
    return getInstance

@singleton
class MotorManager:
    """Object to manage the motor PWM states."""

    started_motors = []

    def __init__(self):
        """Contruct a MotorManager."""
        print "Starting motor manager"

    def set_speed(self, pin, speed):
        """Set the speed of a motor pin."""
        global pwm
        if pin in self.started_motors:
            pwm.set_duty_cycle(pin, speed)
        else:
            pwm.start(pin, speed, DEFAULT_SOFTPWM_FREQ)
            self.started_motors.append(pin)

def run_command(decoded):
    """
    Run the command specified by `decoded`.

    :param decoded:
        The command to run
    """
    print decoded['command']
    global motor_manager
    if decoded['command'] == 'START_MOTOR':
        print decoded['pin']
        print decoded['speed']
        print "Starting motor"
        motor_manager.set_speed(decoded['pin'], float(decoded['speed']))
    elif decoded['command'] == 'STOP_MOTOR':
        print decoded['pin']
        print "Stopping motor"
        motor_manager.set_speed(decoded['pin'], 0)

def set_rovercodeweb_url(base_url):
    """Set the global URL variables for rovercodeweb."""
    global ROVERCODE_WEB_OAUTH2_URL
    global ROVERCODE_WEB_REG_URL
    ROVERCODE_WEB_REG_URL = base_url + "api/v1/rovers"
    ROVERCODE_WEB_OAUTH2_URL = base_url + "oauth2/token"

if __name__ == '__main__':
    print "Starting the rover service!"
    load_dotenv(find_dotenv())
    rovercode_web_url = os.getenv("ROVERCODE_WEB_URL", "https://rovercode.com/")
    if rovercode_web_url[-1:] != '/':
        rovercode_web_url += '/'
    set_rovercodeweb_url(rovercode_web_url)

    client_id = os.getenv('CLIENT_ID', '')
    if client_id == '':
        raise NameError("Please add CLIENT_ID to your .env")
    client_secret = os.getenv('CLIENT_SECRET', '')
    if client_secret == '':
        raise NameError("Please add CLIENT_SECRET to your .env")

    heartbeat_manager = HeartBeatManager(
            client_id= client_id,
            client_secret= client_secret)
    if heartbeat_manager.thread is None:
        heartbeat_manager.thread = socketio.start_background_task(target=heartbeat_manager.thread_func)

    motor_manager = MotorManager()

    socketio.run(app, port=80, host='0.0.0.0')
