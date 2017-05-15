FROM debian:stable

MAINTAINER Clifton Barnes <clifton.a.barnes@gmail.com>

RUN apt-get update
RUN apt-get install -y python python-dev python-pip python-smbus nginx build-essential git libssl-dev
RUN pip install flask flask-socketio gevent uwsgi Sphinx==1.4.8 sphinx_rtd_theme pytest-flask pytest-cov mock requests responses pylint==1.6.5 prospector==0.12.4 flask-cors python-dotenv

EXPOSE 80

ADD www /var/www/rovercode/www
ADD nginx-site /etc/nginx/sites-enabled/rovercode

WORKDIR /etc/nginx/sites-enabled
RUN rm -f default

WORKDIR /var/www/rovercode/www/Adafruit_Python_GPIO
RUN python setup.py install
WORKDIR /var/www/rovercode
RUN git clone -b uwsgi-2.0 https://github.com/unbit/uwsgi.git
WORKDIR /var/www/rovercode/uwsgi
RUN python uwsgiconfig.py --build core
RUN python uwsgiconfig.py --plugin plugins/python core
RUN python uwsgiconfig.py --plugin plugins/corerouter core
RUN python uwsgiconfig.py --plugin plugins/http core
RUN python uwsgiconfig.py --plugin plugins/gevent core
RUN cp uwsgi /var/www/rovercode/www
RUN cp python_plugin.so /var/www/rovercode/www
RUN cp corerouter_plugin.so /var/www/rovercode/www
RUN cp http_plugin.so /var/www/rovercode/www
RUN cp gevent_plugin.so /var/www/rovercode/www
WORKDIR /var/www/rovercode
RUN rm -rf uwsgi
WORKDIR /var/www/rovercode/www
RUN echo '/etc/init.d/nginx start && uwsgi rovercode.ini --plugins python,corerouter,http,gevent --gevent 1000 --http-websockets' > /usr/bin/run.sh
ENTRYPOINT ["bash", "/usr/bin/run.sh"]
