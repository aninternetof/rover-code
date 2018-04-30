#! /bin/bash

INI_DIR=www/
ADAFRUIT_DIR=www/Adafruit_Python_GPIO

if [ "${EUID}" -ne 0 ]; then
	echo "Error: This script must be run as root."
	exit 1
fi

if [ ! -e ${ADAFRUIT_DIR} ]; then
	echo "Error: Adafruit directory not found."
	exit 2
fi

apt-get install -y python python-dev python-pip python-smbus
pip install virtualenv && \
virtualenv --system-site-packages env && \
. env/bin/activate && \
pip install -r www/requirements.txt

pushd ${ADAFRUIT_DIR} > /dev/null
python setup.py install
popd > /dev/null

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
