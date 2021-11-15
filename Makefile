.PHONY: lint

NAME=neuro

run-local-service:
	LOG_VERBOSITY=4 WORKERS=4 neuro


load-test-ui:
	locust

load-test:
	locust --headless -u 1000 -r 100 --run-time 1m

lint:
	pip install isort && isort . --atomic && pip install black && black **/*.py

install:
	pip install -r requirements.dev.txt && pip install -e .

docker-app:
	docker build --tag neuro-docker . && docker run --publish 3003:3003 neuro-docker

client-call:
	python client/example.py

multi-call:
	python client/multiple_calls.py