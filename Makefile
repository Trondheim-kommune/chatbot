install:
	pip install .

setup:
	pip install .

test: setup
	pytest
	flake8 --exclude=venv,build .

