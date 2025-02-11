# Makefile

.PHONY: setup run test docker-build docker-up docker-down

setup:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest

docker-build:
	docker-compose build

docker-up:
	docker-compose up

docker-down:
	docker-compose down