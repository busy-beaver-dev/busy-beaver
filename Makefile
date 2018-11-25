test:
	pytest

test-cov:
	pytest --cov

test-covhtml:
	pytest --cov --cov-report html && open ./htmlcov/index.html

test-skipvcr:
	pytest -m 'not vcr'
