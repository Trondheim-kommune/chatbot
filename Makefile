SHELL := /bin/bash

install:
	source venv/bin/activate && pip install .

test: install
	source venv/bin/activate && TEST_FLAG=TRUE pytest
	source venv/bin/activate && flake8 --exclude=venv,build,website .

test-docker:
	docker exec --env TEST_FLAG=TRUE -it agent25 pytest 
	docker exec -it agent25 flake8 --exclude=venv,build,website .

build:
	source venv/bin/activate && docker-compose build

build-clean:
	source venv/bin/activate && docker-compose build --no-cache

start:
	source venv/bin/activate && docker-compose up -d

build-and-run:
	source venv/bin/activate && docker-compose build && docker-compose up -d

docker-logs:
	docker-compose logs

stop:
	docker-compose stop

make open-bash-agent25:
	docker exec -it agent25 bash

make open-bash-web:
	docker exec -it web bash

