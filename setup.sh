#!/bin/bash
if ! [ -d "venv" ]; then
  virtualenv -p python3 venv
fi
source venv/bin/activate
python setup.py install develop
pip install -r requirements.txt
