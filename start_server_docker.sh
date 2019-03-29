#!/bin/sh
#cd api/flask
#service nginx start
#uwsgi --http :8080 --wsgi-file api/flask/wsgi.py 
#uwsgi --ini uwsgi.ini
cron
./api/flask/start_server.sh 
