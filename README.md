![screenshot](https://rovercode.com/static/images/screenshot.jpg)

# Rovercode

[![Chat](https://img.shields.io/badge/chat-developer-brightgreen.svg?style=flat)](https://rovercode.zulip.com)
[![](https://images.microbadger.com/badges/image/cabarnes/rovercode.svg)](https://microbadger.com/images/cabarnes/rovercode)
[![Build Status](https://travis-ci.org/rovercode/rovercode.svg?branch=development)](https://travis-ci.org/rovercode/rovercode)
[![Coverage Status](https://coveralls.io/repos/github/rovercode/rovercode/badge.svg)](https://coveralls.io/github/rovercode/rovercode)

Rovercode is easy-to-use package for controlling robots (rovers) that can sense and react to their environment. The Blockly editor makes it easy to program and run your bot straight from your browser. Just drag and drop your commands to drive motors, read values from a variety of supported sensors, and see what your rover sees with the built in webcam viewer.

Rovercode runs on any single-board-computer supported by the [Adafruit Python GPIO wrapper library](https://github.com/adafruit/Adafruit_Python_GPIO), including the NextThingCo CHIP, Raspberry Pi, and BeagleBone Black. Once installed, head to to rovercode.com and connect to your rover.

**rovercode is made up of two parts.** rovercode (this repo) is the service that runs on the rover. rovercode-web ([a different repo](https://github.com/rovercode/rovercode-web)) is the web app that is hosted on the Internet.
[Try a live demo.](https://rovercode.com/mission-control)

## Contributing
Check out our [contributing page](http://rovercode.readthedocs.io/en/latest/contribute.html) to get started.

## Setup

### Standard Setup
First, on your rover (CHIP, Raspberry Pi, BeagleBone, etc):
```bash
$ sudo apt install git
$ git clone --recursive https://github.com/rovercode/rovercode.git && cd rovercode
$ sudo bash setup.sh #run this only once -- it will take some time
$ # create your .env, as described in the section below
$ sudo bash start.sh #run this each time you boot the rover (or automatically start if chosen in setup)
```
Then, on any PC or tablet, head to rovercode.com to connect to your rover. Start playing!

### Development PC Setup
When developing rovercode, you may want to run rovercode on your PC instead of a CHIP/Raspberry Pi/Beaglebone. Below are instructions for how to install and run rovercode on your PC. Everything should work fine: rovercode will automatically detect that it is not running on target hardware and will stub out the calls to the motors and sensors.

#### Development PC Standard Setup
First, on your development PC:
```bash
$ sudo apt install git
$ git clone --recursive https://github.com/rovercode/rovercode.git && cd rovercode
$ sudo bash setup.sh #run this only once -- it will take some time
$ # create your .env, as described in the section below
$ sudo bash start.sh #run this each time
```
Then, still on your development PC, head to rovercode.com and connect to your "rover" (your PC running the service).

#### Development PC Alternate Setup (Docker)
Rather use Docker? First, on your development PC:
```bash
$ sudo apt install git docker.io
$ git clone --recursive https://github.com/rovercode/rovercode.git && cd rovercode
$ sudo docker build -t rovercode .
$ # create your .env, as described in the section below
$ sudo docker run --name rovercode -v $PWD:/var/www/rovercode -p 80:80 -d rovercode

```
Then, still on your development PC, head to rovercode.com and connect to your "rover" (your PC running the service).

### Creating Your .env
First, create a rovercode.com account [here](https://rovercode.com/accounts/signup/). Then, navigate to the "My Rovers" section and create a new rover. Once it is created, click the "Download Credentials" button at the bottom of the rover's detail page. Save the credentials file as `.env` in the same directory as this README.

## Play and Contribute
rovercode is usable now, but we have lots of great features left to be added. Check out the [contributing instructions](https://contributor-docs.rovercode.com) then head over to the feature tracker to see if there's something fun to contribute.

## Testing
Run the tests like this:
Make sure the container is running (the `sudo docker run ...` command above), then in another terminal, do:
```bash
$ sudo docker exec -it rovercode bash -c "python -m pytest"
$ sudo docker exec -it rovercode bash -c prospector

```

## Docs
Read the complete docs [here](http://rovercode.readthedocs.io/en/latest).

## Contact

We'd love to chat with you! Join the [our chat!](https://rovercode.zulipchat.com).

## License
[GNU GPLv3](license) © Rovercode LLC and Rovercode contributors
