install:
	pip install -e .

setup: install

test: setup
	pytest
	flake8 --exclude=venv,build .

