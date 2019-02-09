install:
	python setup.py install

test: setup
	pytest

lint:
	flake8 --exclude=venv,build .