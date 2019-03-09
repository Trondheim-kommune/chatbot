#!/bin/bash
source /home/agent25/agent-25/venv/bin/activate
FLASK_APP=api/flask/server.py flask run --host 0.0.0.0 --port=8080
