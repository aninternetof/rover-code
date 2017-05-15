#! /bin/bash

INI_DIR=www/
ADAFRUIT_DIR=www/Adafruit_Python_GPIO
UWSGI_DIR=uwsgi/

if [ "${EUID}" -ne 0 ]; then
	echo "Error: This script must be run as root."
	exit 1
fi

if [ ! -e ${ADAFRUIT_DIR} ]; then
	echo "Error: Adafruit directory not found."
	exit 2
fi

apt-get install -y python python-dev python-pip python-smbus nginx build-essential git libssl-dev
pip install flask flask-socketio gevent uwsgi Sphinx==1.4.8 sphinx_rtd_theme pytest-flask pytest-cov mock requests responses pylint==1.6.5 prospector==0.12.4 flask-cors python-dotenv

pushd ${ADAFRUIT_DIR} > /dev/null
python setup.py install
popd > /dev/null

git clone -b uwsgi-2.0 https://github.com/unbit/uwsgi.git
pushd ${UWSGI_DIR} > /dev/null
python uwsgiconfig.py --build core
python uwsgiconfig.py --plugin plugins/python core
python uwsgiconfig.py --plugin plugins/corerouter core
python uwsgiconfig.py --plugin plugins/http core
python uwsgiconfig.py --plugin plugins/gevent core
popd > /dev/null

cp ${UWSGI_DIR}/uwsgi ${INI_DIR}
cp ${UWSGI_DIR}/python_plugin.so ${INI_DIR}
cp ${UWSGI_DIR}/corerouter_plugin.so ${INI_DIR}
cp ${UWSGI_DIR}/http_plugin.so ${INI_DIR}
cp ${UWSGI_DIR}/gevent_plugin.so ${INI_DIR}
rm -rf ${UWSGI_DIR}

rm -rf /var/www/rovercode > /dev/null
mkdir -p /var/www/rovercode
ln -s $(pwd)/www /var/www/rovercode/www
ln -fs $(pwd)/nginx-site /etc/nginx/sites-enabled/rovercode
rm -rf /etc/nginx/sites-enabled/default > /dev/null
service nginx restart

# Ask the user if they want to start automatically on boot
ask() {
    # http://djm.me/ask
    local prompt default REPLY

    while true; do

        if [ "${2:-}" = "Y" ]; then
            prompt="Y/n"
            default=Y
        elif [ "${2:-}" = "N" ]; then
            prompt="y/N"
            default=N
        else
            prompt="y/n"
            default=
        fi

        # Ask the question (not using "read -p" as it uses stderr not stdout)
        echo -n "$1 [$prompt] "

        # Read the answer (use /dev/tty in case stdin is redirected from somewhere else)
        read REPLY </dev/tty

        # Default?
        if [ -z "$REPLY" ]; then
            REPLY=$default
        fi

        # Check if the reply is valid
        case "$REPLY" in
            Y*|y*) return 0 ;;
            N*|n*) return 1 ;;
        esac

    done
}

if ask "Do you want to automatically start on boot? (choose N for development):"; then
    echo "Going to start on boot..."
    mkdir .backup && cp /etc/rc.local .backup/
    sed -i -e '$i \bash '$(pwd)'\/start.sh \&\n' /etc/rc.local
else
    echo "Not going to start on boot..."
fi

echo "Setup complete."

exit 0
