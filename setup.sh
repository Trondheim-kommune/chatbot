#!/bin/bash
virtualenv -p python3 venv
source venv/bin/activate
pip install .
python setup.py install
pip install -r requirements.txt
