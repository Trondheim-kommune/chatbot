#!/bin/bash
if ! [ -d "venv" ]; then
  virtualenv -p python venv
fi
source venv/Scripts/activate
pip install .
python setup.py install
pip install -r requirements.txt
