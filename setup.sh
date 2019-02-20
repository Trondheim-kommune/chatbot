#!/bin/bash
if ! [ -d "venv" ]; then
  if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    virtualenv -p python3 venv
  elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    virtualenv -p python venv
  fi
fi

if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  source venv/bin/activate
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
  source venv/Scripts/activate
fi

pip install .
python setup.py install
pip install -r requirements.txt
