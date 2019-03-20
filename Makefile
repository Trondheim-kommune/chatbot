install:
	pip install -e .

setup: install

test: setup
	TEST_FLAG=TRUE pytest
	flake8 --exclude=venv,build,website .

