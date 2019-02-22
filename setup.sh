#!/bin/bash
if ! [ -d "venv" ]; then
  if [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    virtualenv -p python venv
    mv venv/Scripts venv/bin
  else
    virtualenv -p python3 venv
  fi
fi

source venv/bin/activate

pip install .
python setup.py install
pip install -r requirements.txt
