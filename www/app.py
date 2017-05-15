"""Rovercode app."""
from flask import Flask, jsonify, Response, request, send_from_directory
from flask_cors import CORS
import requests, json, socket
from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv, find_dotenv
import os
try:
    import Adafruit_GPIO.PWM as pwmLib
    import Adafruit_GPIO.GPIO as gpioLib
except ImportError:
    print "Adafruit_GPIO lib unavailable"


load_dotenv(find_dotenv())
rovercode_web_url = os.getenv("ROVERCODE_WEB_URL", "https://rovercode.com/")
if rovercode_web_url[-1:] != '/':
    rovercode_web_url += '/'

ROVERCODE_WEB_REG_URL = rovercode_web_url + "mission-control/rovers/"

# Let SocketIO choose the best async mode
async_mode = 'gevent_uwsgi'

def create_app():
    """Creator of rovercode flask app."""
    app = Flask(__name__)
    CORS(app, resources={r'/api/*': {"origins": [".*rovercode.com", ".*localhost"]}})
    return app

app = create_app()

create_app()
try:
    socketio = SocketIO(app, async_mode=async_mode)
except:
    # Needed for sphinx documentation
    socketio = SocketIO(app)

ws_thread = None
hb_thread = None
payload = None

try:
    pwm = pwmLib.get_platform_pwm(pwmtype="softpwm")
    gpio = gpioLib.get_platform_gpio()
except NameError:
    print "Adafruit_GPIO lib is unavailable"

DEFAULT_SOFTPWM_FREQ = 100

binary_sensors = []

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

    :param run:
        A flag for the state of the thread. Set to false to gracefully stop
        the thread.
    :param thread:
        The Thread object that performs the periodic check-in.
    :param web_id:
        The rovercode-web id of this rover.
    :param payload:
        The json-formatted information about the rover to send to rovercode-web.
    """

    def __init__(self, payload, id=None):
        """Constructor for the HeartBeatManager."""
        self.run = True
        self.thread = None
        self.web_id = id
        self.payload = payload

    def register(self):
        """Regiser the rover with rovercode-web."""
        print "Registering with rovercode-web"
        r = requests.post(ROVERCODE_WEB_REG_URL, self.payload)
        self.web_id = json.loads(r.text)['id']
        print "rovercode-web id is " + str(self.web_id)
        return r

    def stopThread(self):
        """Gracefully stop the periodic check-in thread."""
        self.run = False

    def thread_func(self, run_once=False):
        """Thread function that periodically checks in with rovercode-web."""
        while self.run:
            print "Checking in with rovercode-web"
            # try:
            print "ID is " + str(self.web_id)
            r = requests.put(ROVERCODE_WEB_REG_URL+str(self.web_id)+"/", self.payload)
            print r
            if r.status_code in [200, 201]:
                print "... success"
            elif r.status_code in [404]:
                #rovercode-web must have forgotten us. Reregister.
                print "... reregistering"
                r = self.register()
                if r.status_code not in [200, 201]:
                    print "... error in reregistering"
            else:
                print "... error"
            # except:
                # print "Could not connect to rovercode-web"
            if run_once:
                break
            socketio.sleep(3)
        print "Exiting heartbeat thread"
        return r

heartbeat_manager = HeartBeatManager(
        payload = {'name': 'Chipy', 'owner': 'Mr. Hurlburt', 'local_ip': get_local_ip()})
heartbeat_manager.register()
if heartbeat_manager.thread is None:
    heartbeat_manager.thread = socketio.start_background_task(target=heartbeat_manager.thread_func)

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

@app.route('/api/v1/blockdiagrams', methods=['GET'])
def get_block_diagrams():
    """
    API: /blockdiagrams [GET].

    Replies with a JSON formatted list of the block diagrams
    """
    names = []
    for f in listdir('saved-bds'):
        if isfile(join('saved-bds', f)) and f.endswith('.xml'):
            names.append(xml.etree.ElementTree.parse(join('saved-bds', f)).getroot().find('designName').text)
    return jsonify(result=names)

@app.route('/api/v1/blockdiagrams', methods=['POST'])
def save_block_diagram():
    """
    API: /blockdiagrams [POST].

    Saves the posted block diagram
    """
    designName = request.form['designName'].replace(' ', '_').replace('.', '_')
    bdString = request.form['bdString']
    root = xml.etree.ElementTree.Element("root")

    xml.etree.ElementTree.SubElement(root, 'designName').text = designName
    xml.etree.ElementTree.SubElement(root, 'bd').text = bdString

    tree = xml.etree.ElementTree.ElementTree(root)
    tree.write('saved-bds/' + designName + '.xml')
    return ('', 200)

@app.route('/api/v1/blockdiagrams/<string:id>', methods=['GET'])
def get_block_diagram(id):
    """
    API: /blockdiagrams/<id> [GET].

    Replies with an XML formatted description of the block diagram specified by
    `id`
    """
    id = id.replace(' ', '_').replace('.', '_')
    bd = [f for f in listdir('saved-bds') if isfile(join('saved-bds', f)) and id in f]
    with open(join('saved-bds',bd[0]), 'r') as content_file:
        content = content_file.read()
    return Response(content, mimetype='text/xml')

@app.route('/api/v1/download/<string:id>', methods = ['GET'])
def download_block_diagram(id):
    """
    API: /download/<id> [GET].

    Starts a download of the block diagram specified by `id`
    """
    if isfile(join('saved-bds', id)):
        return send_from_directory('saved-bds', id, mimetype='text/xml', as_attachment=True)
    else:
        return ('', 404)

@app.route('/api/v1/upload', methods = ['POST'])
def upload_block_diagram():
    """
    API: /upload [POST].

    Adds the posted block diagram
    """
    if 'fileToUpload' not in request.files:
        return ('', 400)
    file = request.files['fileToUpload']
    filename = file.filename.rsplit('.', 1)[0]
    suffix = 0
    # Check if there already is a design with this name
    while isfile(join('saved-bds', filename + '.xml')):
        suffix += 1
        # Append _# to the design name to make it unique
        if (suffix > 1):
            filename = filename.rsplit('_', 1)[0]
        filename += '_' + str(suffix)
    # Ensure that the design name is the same as the file name
    root = xml.etree.ElementTree.fromstring(file.read())
    designName = root.find('designName')
    designName.text = filename
    tree = xml.etree.ElementTree.ElementTree(root)
    tree.write(join('saved-bds', filename + '.xml'))
    return ('', 200)

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

def init_rover_service():
    """Initialize hardware pins and motor speeds."""
    # set up IR sensor gpio
    gpio.setup("XIO-P2", gpioLib.IN)
    gpio.setup("XIO-P4", gpioLib.IN)
    global binary_sensors
    binary_sensors.append(BinarySensor("right_ir_sensor", "XIO-P4", 'rightEyeUncovered', 'rightEyeCovered'))
    binary_sensors.append(BinarySensor("left_ir_sensor", "XIO-P2", 'leftEyeUncovered', 'leftEyeCovered'))

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

try:
    init_rover_service()
except NameError:
    print "Adafruit_GPIO lib is unavailable"

motor_manager = MotorManager()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
