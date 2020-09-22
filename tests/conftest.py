"""Project wide pytest plugins / fixtures

References:
    - http://alexmic.net/flask-sqlalchemy-pytest/
    - http://flask.pocoo.org/docs/1.0/testing/
"""

import pytest

from busy_beaver.extensions import rq as _rq

pytest_plugins = (
    "tests._utilities.fixtures.database",
    "tests._utilities.fixtures.flask",
    "tests._utilities.fixtures.toolbox",
    "tests._utilities.fixtures.vcr",
)


@pytest.fixture(scope="module")
def rq(app):
    yield _rq
