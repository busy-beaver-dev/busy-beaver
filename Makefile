help:
	@echo 'Makefile for managing application                                  '
	@echo '                                                                   '
	@echo 'Usage:                                                             '
	@echo ' make build            rebuild containers .                        '
	@echo ' make up               start local dev environment                 '
	@echo ' make down             stop local dev environment                  '
	@echo ' make migration        create migration m="message"                '
	@echo ' make migrate-up       run all migration                           '
	@echo ' make migrate-dow      roll back last migration                    '
	@echo ' make test             run tests                                   '
	@echo ' make test-cov         run tests with coverage.py                  '
	@echo ' make test-covhtml     run tests and load html coverage report     '
	@echo ' make test-skipvcr     run non-vcr tests                           '
	@echo ' make lint             run flake8 linter                           '
	@echo '                                                                   '
	@echo ' make shell            log into into app container -- bash-shell   '
	@echo ' make shell-dev        open ipython shell with application context '
	@echo ' make ngrok            start ngrok to forward port                 '
	@echo '                                                                   '
	@echo ' make prod-build       build production images                     '
	@echo ' make prod-up          start prod environment                      '
	@echo ' make prod-down        stop prod environment                       '
	@echo ' make prod-pull-imge   pull latest deployment image                '
	@echo ' make prod-deploy      redeploy application                        '
	@echo '                                                                   '

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

migration: ## Create migrations using alembic
	docker-compose exec app alembic --config=./migrations/alembic.ini revision --autogenerate -m "$(m)"

migrate-up: ## Run migrations using alembic
	docker-compose exec app alembic --config=./migrations/alembic.ini upgrade head

migrate-down: ## Rollback migrations using alembic
	docker-compose exec app alembic --config=./migrations/alembic.ini downgrade -1

test:
	docker-compose exec app pytest

test-cov:
	docker-compose exec app pytest --cov ./

test-covhtml:
	docker-compose exec app pytest --cov --cov-report html && open ./htmlcov/index.html

test-skipvcr:
	docker-compose exec app pytest -m 'not vcr'

lint:
	docker-compose exec app flake8

shell:
	docker-compose exec app bash

shell-dev:
	docker-compose exec app ipython -i scripts/dev_shell.py

ngrok:
	ngrok http 5000

prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-pull-image:
	docker pull alysivji/busy-beaver:latest

prod-deploy: prod-pull-image
	make prod-down
	make prod-up
