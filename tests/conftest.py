"""Project wide pytest plugins / fixtures

References:
    - http://alexmic.net/flask-sqlalchemy-pytest/
    - http://flask.pocoo.org/docs/1.0/testing/
"""

from datetime import timedelta
import pytest

from busy_beaver.adapters import KeyValueStoreAdapter
from busy_beaver.app import create_app
from busy_beaver.extensions import db as _db, rq as _rq
from busy_beaver.models import ApiUser
from busy_beaver.toolbox import utc_now_minus


@pytest.fixture(scope="session")
def vcr_config():
    return {"filter_headers": [("authorization", "DUMMY")]}


@pytest.fixture(scope="session")
def app():
    """Session-wide test `Flask` application.

    Establish an application context before running the tests.
    """
    app = create_app(testing=True)
    ctx = app.app_context()
    ctx.push()
    yield app

    ctx.pop()


@pytest.fixture(scope="session")
def client(app):
    """Create flask test client where we can trigger test requests to app"""
    client = app.test_client()
    yield client


@pytest.fixture(scope="session")
def db(app):
    """Session-wide test database."""
    _db.app = app
    _db.create_all()
    yield _db

    _db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})

    session = db.create_scoped_session(options=options)
    db.session = session
    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def kv_store(session):
    return KeyValueStoreAdapter()


@pytest.fixture(scope="session")
def rq(app):
    yield _rq


@pytest.fixture
def patcher(monkeypatch):
    """Helper to patch in the correct spot"""

    def _patcher(module_to_test, *, namespace, replacement):
        namespace_to_patch = f"{module_to_test}.{namespace}"
        monkeypatch.setattr(namespace_to_patch, replacement)
        return replacement

    yield _patcher


@pytest.fixture
def t_minus_one_day():
    return utc_now_minus(timedelta(days=1))


@pytest.fixture
def create_api_user(session):
    def _new_api_user(username, *, token="abcd", role="user"):
        new_api_user = ApiUser(username=username, token=token, role=role)
        session.add(new_api_user)
        session.commit()
        return new_api_user

    return _new_api_user
