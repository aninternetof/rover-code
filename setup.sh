#! /bin/bash

ADAFRUIT_DIR=www/Adafruit_Python_GPIO

if [ "${EUID}" -ne 0 ]; then
	echo "Error: This script must be run as root."
	exit 1
fi

if [ ! -e ${ADAFRUIT_DIR} ]; then
	echo "Error: Adafruit directory not found."
	exit 2
fi

apt-get install -y python python-dev python-pip python-smbus nginx uwsgi uwsgi-plugin-python
pip install flask flask-socketio

pushd ${ADAFRUIT_DIR} > /dev/null
python setup.py install
popd > /dev/null

rm -rf /var/www/rovercode > /dev/null
mkdir -p /var/www/rovercode
ln -s $(pwd)/www /var/www/rovercode/www
ln -fs $(pwd)/nginx-site /etc/nginx/sites-enabled/rovercode
service nginx restart

echo "Setup complete."

exit 0
