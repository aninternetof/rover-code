Setup
========

Setup on the rover
-----------------------
First, on your rover (Raspberry Pi, CHIP, etc):

.. code-block:: bash

    $ sudo apt install git
    $ git clone --recursive https://github.com/rovercode/rovercode.git && cd rovercode
    $ sudo bash setup.sh #run this only once -- it will take some time
    $ # create your .env, as described in the section below
    $ sudo bash start.sh #run this each time you boot the rover (or automatically start if chosen in setup)

Then, on any PC or tablet, head to rovercode.com to connect to your rover. Start playing!

Development PC Setup
------------------------
When developing rovercode, you may want to run rovercode on your PC instead of a CHIP/Raspberry Pi/Beaglebone.
Below are instructions for how to install and run rovercode on your PC. Don't worry about hardware-specific things
like I2C: rovercode will automatically detect that it is not running on target hardware and will stub out the calls to the motors 
and sensors.

First, on your development PC:

.. code-block:: bash

    $ sudo apt install git docker.io
    $ git clone --recursive https://github.com/rovercode/rovercode.git && cd rovercode
    $ sudo docker build -t rovercode .
    $ # create your .env, as described in the section below
    $ sudo docker run --name rovercode -v $PWD:/var/www/rovercode -p 80:80 -d rovercode

Creating Your .env
-----------------------
First, create a rovercode.com account [here](https://rovercode.com/accounts/signup/). Then, navigate to the "My Rovers" section and
create a new rover. Once it is created, click the "Download Credentials" button at the bottom of the rover's detail page. The file
will download as something like `rovercode_yourrovername.env`. Rename the file as only `.env` (nothing before the dot) and save it in the same directory as this README.

Something Not Working?
--------------------------
If something in these instructions is not working right for you, you can get help in [our Gitter chatroom](https://gitter.im/rovercode/Lobby). Or, if you think it might be a bug, you can [file a ticket](https://github.com/rovercode/rovercode/issues/new).

