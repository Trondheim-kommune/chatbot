#!/bin/sh
cd api/flask
FLASK_APP=server.py flask run --host 0.0.0.0 --port=8080
