install:
	pip install .

test: install
	TEST_FLAG=TRUE pytest
	flake8 --exclude=venv,build,website .

make build:
	docker-compose build

make build-clean:
	docker-compose build --no-cache

make start:
	docker-compose up


