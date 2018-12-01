help:
	@echo 'Makefile for managing application                                  '
	@echo '                                                                   '
	@echo 'Usage:                                                             '
	@echo ' make migration        create migration m="message"                '
	@echo ' make migrate-up       run all migration                           '
	@echo ' make migrate-dow      roll back last migration                    '
	@echo ' make test             run tests                                   '
	@echo ' make test-cov         run tests with coverage.py                  '
	@echo ' make test-fast        run tests without migrations                '
	@echo ' make lint             run flake8 linter                           '
	@echo '                                                                   '
	@echo ' make shell            open ipython shell with application context '
	@echo ' make shell-db         shell into psql inside database container   '
	@echo '                                                                   '


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
	docker-compose exec app ipython -i scripts/dev_shell.py

# serve:
# 	uvicorn busy_beaver.backend:api --host 0.0.0.0 --port 5100 --debug

# ngrok:
# 	ngrok http 5100
