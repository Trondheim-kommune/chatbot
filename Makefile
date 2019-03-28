install:
	pip install .

test: install
	TEST_FLAG=TRUE pytest
	flake8 --exclude=venv,build,website .

