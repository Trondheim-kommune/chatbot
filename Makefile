install:
	pip install .

setup:
	pip install .

test: setup
	pytest

lint:
	flake8 --exclude=venv,build .
