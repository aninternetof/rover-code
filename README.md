![screenshot](https://rovercode.com/static/images/screenshot.jpg)

# rovercode

[![Gitter](https://badges.gitter.im/rovercode.png)](https://gitter.im/rovercode/Lobby)
[![Build Status](https://travis-ci.org/rovercode/rovercode.svg?branch=development)](https://travis-ci.org/rovercode/rovercode)
[![Coverage Status](https://coveralls.io/repos/github/rovercode/rovercode/badge.svg)](https://coveralls.io/github/rovercode/rovercode)

rovercode is an open-source educational robotics platform. Students use our web-based drag-and-drop editor to create
code that listens to the rover's sensors and controls its motors.

rovercode is made up of serveral code repositories. You are currently viewing `rovercode`, the service that runs
on the rover itself. It listens for commands from the web application to control the rover's motors, and it monitors the rover's sensors and sends their values up to the web application. The service can run on most single-board-computers and is 
officially tested with the Raspberry Pi 3, Raspberry Pi Zero W, and the Next Thing Co. CHIP.

To learn about the other pieces of rovercode, visit our [architecture documentation](https://contributor-docs.rovercode.com/architecture.html), or start at [the root of rovercode's documentation](https://contributor-docs.rovercode.com).

## Setup

### Setup on the rover
First, on your rover (Raspberry Pi, CHIP, etc):
```bash
$ sudo apt install git
$ git clone --recursive https://github.com/rovercode/rovercode.git && cd rovercode
$ sudo bash setup.sh #run this only once -- it will take some time
$ # create your .env, as described in the section below
$ sudo bash start.sh #run this each time you boot the rover (or automatically start if chosen in setup)
```
Then, on any PC or tablet, head to rovercode.com to connect to your rover. Start playing!

### Development PC Setup
When developing rovercode, you may want to run rovercode on your PC instead of a CHIP/Raspberry Pi/Beaglebone.
Below are instructions for how to install and run rovercode on your PC. Don't worry about hardware-specific things
like I2C: rovercode will automatically detect that it is not running on target hardware and will stub out the calls to the motors 
and sensors.

First, on your development PC:
```bash
$ sudo apt install git docker.io
$ git clone --recursive https://github.com/rovercode/rovercode.git && cd rovercode
$ sudo docker build -t rovercode .
$ # create your .env, as described in the section below
$ sudo docker run --name rovercode -v $PWD:/var/www/rovercode -p 80:80 -d rovercode
```

### Creating Your .env
First, create a rovercode.com account [here](https://rovercode.com/accounts/signup/). Then, navigate to the "My Rovers" section and
create a new rover. Once it is created, click the "Download Credentials" button at the bottom of the rover's detail page. The file
will download as something like `rovercode_yourrovername.env`. Rename the file as only `.env` (nothing before the dot) and save it in the same directory as this README.

### Something Not Working?
If something in these instructions is not working right for you, you can get help in [our Gitter chatroom](https://gitter.im/rovercode/Lobby). Or, if you think it might be a bug, you can [file a ticket](https://github.com/rovercode/rovercode/issues/new).


## Docs
More detailed usage instructions can be found [here](https://contributor-docs.rovercode.com/rovercode/master/setup.html).

Read the complete docs [here](https://contributor-docs.rovercode.com).

## Contributing
Help make rovercode better! Check out the [contributing guide](https://contributor-docs.rovercode.com/contributing.html). 

We'd love to chat with you! Say hello in [our Gitter room](https://gitter.im/rovercode/Lobby).

You can also email developers@rovercode.com.

## Docs
Read the complete docs [here](http://rovercode.readthedocs.io/en/latest).

## Contact
Please join the rovercode developer mailing list! [Go here](https://1988.onlinegroups.net/groups/rovercode-developers/), then
click "register".

Also, we'd love to chat with you! Join the [the rovercode Slack channel](http://chat.rovercode.com).

You can also email brady@rovercode.com.

## License
[GNU GPLv3](license) © Brady L. Hurlburt and rovercode contributors
