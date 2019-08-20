install:
	pip install .

test: install
	TEST_FLAG=TRUE python -m pytest
	flake8 --exclude=venv,build,chatbot/website .

test-docker:
	docker exec --env TEST_FLAG=TRUE -it chatbot pytest 
	docker exec -it chatbot flake8 --exclude=venv,build,chatbot/website .

build:
	docker-compose build

build-clean:
	docker-compose build --no-cache

start:
	docker-compose up -d

build-and-run:
	docker-compose build && docker-compose up -d

docker-logs:
	docker-compose logs

stop:
	docker-compose stop

make open-bash-chatbot:
	docker exec -it chatbot bash

make open-bash-web:
	docker exec -it web bash

make evaluate:
	python chatbot/nlp/test/evaluation.py

make run-dev:
	python chatbot/prototype.py

make run-api-server:
	bash chatbot/api/start_server.sh

make run-website:
	cd chatbot/web && npm start
