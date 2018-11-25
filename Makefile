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
	@echo ' make shell-ipython    connect to api container in new bash shell  '
	@echo ' make shell-db         shell into psql inside database container   '
	@echo '                                                                   '


migration: ## Create migrations using alembic
	alembic revision --autogenerate -m "$(m)"

migrate-up: ## Run migrations using alembic
	alembic upgrade head

migrate-down: ## Rollback migrations using alembic
	alembic downgrade -1

test:
	pytest

test-cov:
	pytest --cov

test-covhtml:
	pytest --cov --cov-report html && open ./htmlcov/index.html

test-skipvcr:
	pytest -m 'not vcr'

lint:
	flake8

shell-ipython:
	python `pwd`/scripts/ipython_shell.py