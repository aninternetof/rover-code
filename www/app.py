from flask import Flask, jsonify, Response, request, send_from_directory
from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree
from flask_socketio import SocketIO, emit
import Adafruit_GPIO.PWM as pwmLib
import Adafruit_GPIO.GPIO as gpioLib

# Let SocketIO choose the best async mode
async_mode = None
app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None

pwm = pwmLib.get_platform_pwm(pwmtype="softpwm")
gpio = gpioLib.get_platform_gpio();

binary_sensors = []

class BinarySensor:
    def __init__(self, name, pin, rising_event, falling_event):
        self.name = name
        self.pin = pin
        self.rising_event = rising_event
        self.falling_event = falling_event
        self.old_val = False

def sensors_thread():
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
def test_connect():
    global thread
    print 'Websocket connected'
    if thread is None:
        thread = socketio.start_background_task(target=sensors_thread)
    emit('status', {'data': 'Connected'})

@socketio.on('status', namespace='/api/v1')
def test_message(message):
    print "Got a status message: " + message['data']

@app.route('/api/v1/blockdiagrams', methods=['GET'])
def get_block_diagrams():
    names = []
    for f in listdir('saved-bds'):
        if isfile(join('saved-bds', f)) and f.endswith('.xml'):
            names.append(xml.etree.ElementTree.parse(join('saved-bds', f)).getroot().find('designName').text)
    return jsonify(result=names)

@app.route('/api/v1/blockdiagrams', methods=['POST'])
def save_block_diagram():
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
    id = id.replace(' ', '_').replace('.', '_')
    bd = [f for f in listdir('saved-bds') if isfile(join('saved-bds', f)) and id in f]
    with open(join('saved-bds',bd[0]), 'r') as content_file:
        content = content_file.read()
    return Response(content, mimetype='text/xml')

@app.route('/api/v1/download/<string:id>', methods = ['GET'])
def download_block_diagram(id):
    if isfile(join('saved-bds', id)):
        return send_from_directory('saved-bds', id, mimetype='text/xml', as_attachment=True)
    else:
        return ('', 404)

@app.route('/api/v1/sendcommand', methods = ['POST'])
def send_command():
    run_command(request.form)
    return jsonify(request.form)

def init_rover_service():
    # set up motor pwm
    pwm.start("XIO-P0", 0);
    pwm.start("XIO-P1", 0);
    pwm.start("XIO-P6", 0);
    pwm.start("XIO-P7", 0);

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

def run_command(decoded):
    print decoded['command']
    if decoded['command'] == 'START_MOTOR':
        print decoded['pin']
        print decoded['speed']
        print "Starting motor"
        pwm.set_duty_cycle(decoded['pin'], float(decoded['speed']))
    elif decoded['command'] == 'STOP_MOTOR':
        print decoded['pin']
        print "Stopping motor"
        pwm.set_duty_cycle(decoded['pin'], 0)

init_rover_service()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
