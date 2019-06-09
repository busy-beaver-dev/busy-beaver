.PHONY: help

help: ## This help
	@echo "Makefile for managing application:\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## rebuild containers
	docker-compose build

up: ## start local dev environment
	docker-compose up -d
	make migrate-up

down: ## stop local dev environment
	docker-compose down

restart: ## restart local dev environment
	docker-compose restart $(args)

attach: ## attach to process for debugging purposes
	docker attach `docker-compose ps -q app`

migration: ## create migration m="message"
	docker-compose exec app flask db migrate -m "$(m)"

migration-empty: ## create empty migration m="message
	docker-compose exec app flask db revision -m "$(m)"

migrate-up: ## run all migration
	docker-compose exec app flask db upgrade

migrate-down: ## roll back last migration
	docker-compose exec app flask db downgrade

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

lint: ## run flake8 linter
	docker-compose exec app flake8

log: ## attach to logs
	docker logs `docker-compose ps -q app`

debug: ## attach to app container for debugging
	docker attach `docker-compose ps -q app`

shell: ## log into into app container -- bash-shell
	docker-compose exec app bash

shell-db:  ## log into database container -- psql
	docker-compose exec db psql -w --username "bbdev_user" --dbname "busy-beaver"

shell-dev: ## open ipython shell with application context
	docker-compose exec app ipython -i scripts/dev/shell.py

dev-shell: shell-dev

devshell: shell-dev

ngrok: ## start ngrok to forward port
	ngrok http 5000

prod-build-image:
	docker build -f docker/prod/Dockerfile --tag alysivji/busy-beaver .

prod-build: ## build production images
	docker-compose -f docker-compose.prod.yml build

prod-backup-db:
	docker-compose -f docker-compose.prod.yml exec db pg_dump -U ${POSTGRES_USER} busy-beaver > /tmp/data_dump.sql

prod-upload-backup-to-s3:
	docker run --rm -t \
		-v ${HOME}/.aws:/home/worker/.aws:ro \
		-v `pwd`/scripts/prod:/work \
		-v /tmp/data_dump.sql:/tmp/data_dump.sql \
		shinofara/docker-boto3 python /work/upload_db_backup_to_s3.py

prod-migrate-up:
	docker-compose -f docker-compose.prod.yml exec app flask db upgrade

prod-up: ## start prod environment
	docker-compose -f docker-compose.prod.yml up -d
	make prod-migrate-up

prod-down: ## stop prod environment
	docker-compose -f docker-compose.prod.yml down

prod-pull-image: ## pull latest deployment image
	docker pull alysivji/busy-beaver:latest

prod-deploy: prod-pull-image ## redeploy application
	make prod-down
	make prod-up

prod-shell-db:
	docker-compose -f docker-compose.prod.yml exec db psql -w --username "${POSTGRES_USER}" --dbname "busy-beaver"
