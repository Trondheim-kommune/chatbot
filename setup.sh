#!/bin/bash
virtualenv -p python3 venv
source venv/bin/activate
python3 setup.py install
pip install -r requirements.txt
