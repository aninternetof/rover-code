![screenshot](http://rovercode.org/img/screenshot.jpg)

# rovercode

[![Slack](https://img.shields.io/badge/chat-on%20Slack-41AB8C.svg?style=flat)](https://rovercode.slack.com)
[![MailingList](https://img.shields.io/badge/join-mailing%20list-yellow.svg?style=flat)](http://rovercode.org/cgi-bin/mailman/listinfo/developers)
[![](https://images.microbadger.com/badges/image/cabarnes/rovercode.svg)](https://microbadger.com/images/cabarnes/rovercode)
[![Build Status](https://travis-ci.org/aninternetof/rovercode.svg)](https://travis-ci.org/aninternetof/rovercode)
[![Coverage Status](https://coveralls.io/repos/github/aninternetof/rovercode/badge.svg)](https://coveralls.io/github/aninternetof/rovercode)

rovercode is easy-to-use package for controlling robots (rovers) that can sense and react to their environment. The Blockly editor makes it easy to program and run your bot straight from your browser. Just drag and drop your commands to drive motors, read values from a variety of supported sensors, and see what your rover sees with the built in webcam viewer.

rovercode runs on any single-board-computer supported by the [Adafruit Python GPIO wrapper library](https://github.com/adafruit/Adafruit_Python_GPIO), including the NextThingCo CHIP, Raspberry Pi, and BeagleBone Black. Once installed, head to to rovercode.org and connect to your rover.

**rovercode is made up of two parts.** rovercode (this repo) is the service that runs on the rover. rovercode-web ([a different repo](https://github.com/aninterentof/rovercode)) is the web app that is hosted on the Internet.
[Try a live demo.](http://codetherover.com/demo/rover-code/www/mission-control.html)
## Setup

### Standard Setup
First, on your rover (CHIP, Raspberry Pi, BeagleBone, etc):
```bash
$ sudo apt install git
$ git clone --recursive https://github.com/aninternetof/rovercode.git && cd rovercode
$ sudo ./setup.sh #run this only once -- it will take some time
$ sudo ./start.sh #run this each time you boot the rover
```
Then, on any PC or tablet, head to rovercode.org to connect to your rover. Start playing!

### Development PC Setup
When developing rovercode, you may want to run rovercode on your PC instead of a CHIP/Raspberry Pi/Beaglebone. Below are instructions for how to install and run rovercode on your PC. Everything should work fine: rovercode will automatically detect that it is not running on target hardware and will stub out the calls to the motors and sensors.

#### Development PC Standard Setup
First, on your development PC:
```bash
$ sudo apt install git
$ git clone --recursive https://github.com/aninternetof/rovercode.git && cd rovercode
$ sudo ./setup.sh #run this only once -- it will take some time
$ sudo ./start.sh #run this each time
```
Then, still on your development PC, head to rovercode.org and connect to your "rover" (your PC running the service).

#### Development PC Alternate Setup (Docker)
Rather use Docker? First, on your development PC:
```bash
$ sudo apt install git docker.io
$ git clone --recursive https://github.com/aninternetof/rovercode.git && cd rovercode
$ sudo docker build -t rovercode .
$ sudo docker run --name rovercode -v $PWD:/var/www/rovercode -p 80:80 -d rovercode

```
Then, still on your development PC, head to rovercode.org and connect to your "rover" (your PC running the service).

## Play and Contribute
rovercode is usable now, but we have lots of great features left to be added. Check out the [contributing instructions](https://github.com/aninternetof/rovercode/wiki/Contributing) then head over to the [feature tracker](https://github.com/aninternetof/rovercode/projects/2) to see if there's something fun to contribute.

## Testing
Run the tests like this:
```bash
$ pwd
> ~/rovercode
$ py.test
```
We're having some trouble running pytest-cov inside the Docker container. If you are using Docker for development and want to run test, you'll need to `pip install pytest pytest-cov` outside and run the `py.test` outside of Docker for now.

## License
[GNU GPLv3](license) © Brady L. Hurlburt and the rovercode.org community
