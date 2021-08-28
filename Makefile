.PHONY: help logs

help: ## This help
	@echo "Makefile for managing application:\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

###################
# Local Development
###################
build: ## rebuild containers
	docker-compose build

up: ## start local dev environment; run migrations; populate database
	docker-compose up -d
	make s3-bucket
	make migrate-up
	make populate-db

down: ## stop local dev environment
	docker-compose down

restart: ## restart local dev environment
	docker-compose restart $(args)

attach: ## attach to webserver process for debugging purposes
	docker attach `docker-compose ps -q app`

attach-worker: ## attach to worker process for debugging purposes
	docker attach `docker-compose ps -q worker`

requirements: ## generate requirements.txt using piptools
	pip-compile --output-file=requirements.txt requirements.in

install:  ## install development requirements
	pip install -r requirements_dev.txt

s3-bucket: ## create s3 bucket in localstack
	docker-compose exec -T localstack bash /tmp/dev_scripts/create_s3_bucket.sh

###################
# Database Commands
###################
migration: ## create migration m="message"
	docker-compose exec app flask db migrate -m "$(m)"

migration-empty: ## create empty migration m="message
	docker-compose exec app flask db revision -m "$(m)"

migrate-up: ## run all migration
	docker-compose exec app flask db upgrade

migrate-down: ## roll back last migration
	docker-compose exec app flask db downgrade

dropdb:  ## drop all tables in development database
	psql -d postgresql://bbdev_user:bbdev_password@localhost:9432/busy-beaver -f ./scripts/database/drop_all_tables.sql

populate-db:  ## populate database
	docker-compose exec app python scripts/dev/populate_database.py

#########
# Testing
#########
test: ## run tests
	docker-compose exec app pytest $(args)

test-cov: ## run tests with coverage.py
	docker-compose exec app pytest --cov ./busy_beaver $(args)

test-covhtml: ## run tests and load html coverage report
	docker-compose exec app pytest --cov ./busy_beaver --cov-report html && open ./htmlcov/index.html

test-pdb:
	docker-compose exec app pytest --pdb -s

test-skipvcr: ## run non-vcr tests
	docker-compose exec app pytest -m 'not vcr'

test-curr: ## run all tests marked as `current`
	docker-compose exec app pytest -m 'current'

lint: ## run flake8 linter
	docker-compose exec app flake8

logs: ## attach to logs
	docker-compose logs

#######
# Shell
#######
shell: ## log into into app container -- bash-shell
	docker-compose exec app bash

shell-db:  ## log into database container -- psql
	docker-compose exec db psql -w --username "bbdev_user" --dbname "busy-beaver"

flaskshell:  ## open ipython shell with application context
	docker-compose exec app flask shell

flaskcli:  ## use flask cli to run commands args='args'te
	docker-compose exec app flask $(args)

shell-redis:  ## log into redis container -- rediscli
	docker-compose exec redis redis-cli

###############
# Miscellaneous
###############
changelog:  ## create changelog since release v="version"
	python scripts/generate_changelog.py --version $(v)

ngrok: ## start ngrok to forward port
	ngrok http 5000

pull-upstream: ## pull from upstream master
	git pull upstream master
