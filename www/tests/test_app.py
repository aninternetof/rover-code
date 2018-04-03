"""Test the app module."""
import responses
import re

TEST_URL = "http://a.com/"

def test_sensor_init(testapp):
    """Test the initialization of the sensors."""
    testapp.init_input_gpio('Pin-A', 'Pin-B')
    assert len(testapp.binary_sensors) == 2
    assert testapp.binary_sensors[0].pin == 'Pin-A'
    assert testapp.binary_sensors[1].pin == 'Pin-B'

def test_get_local_ip(testapp):
    """Test that the rover can get its local ip address."""
    # quick and dirty test that it gets something of the form X.X.X.X
    assert len(testapp.get_local_ip().split('.')) == 4

@responses.activate
def test_register_with_web_create(testapp):
    """Test the rover registering with rovercode-web."""
    testapp.set_rovercodeweb_url(TEST_URL)
    testapp.rover_name = "curiosity"
    payload = {'name': 'Chipy',
               'local_ip': '2.2.2.2'}
    web_id = 333
    access_token = '1234'
    testapp.binary_sensors = []
    response_payload = payload.copy()
    response_payload['id'] = web_id

    responses.add(responses.POST, testapp.ROVERCODE_WEB_OAUTH2_URL + '/',
                  json={'access_token': access_token}, status=200,
                  content_type='application/json',
    )
    responses.add(responses.POST, testapp.ROVERCODE_WEB_OAUTH2_URL + '/',
                  json='', status=200,
                  content_type='application/json',
    )
    responses.add(responses.POST, testapp.ROVERCODE_WEB_REG_URL + '/',
                  json=response_payload, status=200,
                  content_type='application/json'
    )

    #test init()
    heartbeat_manager = testapp.HeartBeatManager(client_id='xxxx',
                                                 client_secret="asdf")
    assert access_token in heartbeat_manager.auth_header['Authorization']
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == testapp.ROVERCODE_WEB_OAUTH2_URL + '/'


@responses.activate
def test_register_with_web_update(testapp):
    """Test the periodic hearbeat for a rover that is already registered."""
    testapp.set_rovercodeweb_url(TEST_URL)
    testapp.rover_name = "curiosity"
    testapp.binary_sensors = []
    web_id = '444'
    payload = {'name': testapp.rover_name,
               'web_id': web_id,
               'left_eye_pin': 'Pin-A',
               'right_eye_pin': 'Pin-B',
               'local_ip': '2.2.2.2'}
    access_token = '1234'
    response_payload = payload.copy()
    response_payload['id'] = web_id

    responses.add(responses.POST, testapp.ROVERCODE_WEB_OAUTH2_URL + '/',
                  json={'access_token': access_token}, status=200,
                  content_type='application/json',
    )
    responses.add(responses.POST, testapp.ROVERCODE_WEB_REG_URL + '/',
                  json=response_payload, status=200,
                  content_type='application/json'
    )
    url_re = re.compile(testapp.ROVERCODE_WEB_REG_URL + r'\?oauth_application__client_id=xxxx')
    response_list = [response_payload]
    responses.add(responses.GET,
                  url_re,
                  json=response_list, status=200,
                  content_type='application/json'
    )
    responses.add(responses.PUT, testapp.ROVERCODE_WEB_REG_URL+'/'+str(web_id)+'/',
                  json=response_payload, status=200,
                  content_type='application/json'
    )

    heartbeat_manager = testapp.HeartBeatManager(client_id='xxxx',
                                                 client_secret="asdf")
    heartbeat_manager.thread_func(run_once=True)
    # test the side-effects of read()
    assert heartbeat_manager.web_id == web_id
    assert len(testapp.binary_sensors) == 2
    assert testapp.binary_sensors[0].pin == 'Pin-A'
    assert testapp.binary_sensors[1].pin == 'Pin-B'
    assert len(responses.calls) == 3
    assert responses.calls[0].request.url == testapp.ROVERCODE_WEB_OAUTH2_URL + '/'
    assert responses.calls[1].request.url == testapp.ROVERCODE_WEB_REG_URL + '?oauth_application__client_id=xxxx'
    # test that the update happened
    assert responses.calls[2].request.url == testapp.ROVERCODE_WEB_REG_URL + '/' + str(web_id)+'/'
