function initApi(interpreter, scope) {

	// Add an API function for the alert() block.
	var wrapper = function(text) {
		text = text ? text.toString() : '';
		return interpreter.createPrimitive(writeToConsole(text));
	};
	interpreter.setProperty(scope, 'alert',
		interpreter.createNativeFunction(wrapper));

	// Add an API function for highlighting blocks.
	wrapper = function(id) {
		id = id ? id.toString() : '';
		return interpreter.createPrimitive(highlightBlock(id));
	};
	interpreter.setProperty(scope, 'highlightBlock',
		interpreter.createNativeFunction(wrapper));

	// Add test API function for AJAX
	wrapper = function(text) {
		$.ajax({
			url:'process.php',
			complete: function (response) {
				writeToConsole(response.responseText);
			},
			error: function () {
				$('#consoleArea').append('Bummer: there was an error!');
			}
		});
		return false;
	};
	interpreter.setProperty(scope, 'callMyPHP',
		interpreter.createNativeFunction(wrapper));

	// Add set motor API function
	wrapper = function(motor, direction, speed) {
		// TODO: get pin for motor
		//sendMotorCommand('START', 5, 'FORWARD', 42);
		writeToConsole(motor);
		writeToConsole(direction);
		writeToConsole(speed);
		if (direction.data  == 'FORWARD')
			pin = 'XIO-P7';
		else {
			pin = 'XIO-P5'
		}
		sendMotorCommand('START_MOTOR', pin, speed.data);
		return false;
	};
	interpreter.setProperty(scope, 'setMotor',
		interpreter.createNativeFunction(wrapper));

	// Add stop motor API function
	wrapper = function(motor) {
		// TODO: get pin for motor from actual datastructure
		/* Stop both forward and backward pins, just to be safe */
		sendMotorCommand('STOP_MOTOR', XIO-P7, 0)
		sendMotorCommand('STOP_MOTOR', XIO-P5, 0)
		writeToConsole(motor);
		return false;
	};
	interpreter.setProperty(scope, 'stopMotor',
		interpreter.createNativeFunction(wrapper));

	// Add test API function for popping the event queue
	wrapper = function(text) {
		return interpreter.createPrimitive('myEvent');
	};
	interpreter.setProperty(scope, 'popEventQueue',
		interpreter.createNativeFunction(wrapper));
}
