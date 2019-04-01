install:
	pip install .

test: install
	TEST_FLAG=TRUE pytest
	flake8 --exclude=venv,build,website .

test-docker:
	docker exec -it agent25 pytest

build:
	docker-compose build

build-clean:
	docker-compose build --no-cache

start:
	docker-compose up

build-and-run:
	docker-compose build && docker-compose up

stop:
	docker-compose stop

make open-bash-agent25:
	docker exec -it agent25 bash
