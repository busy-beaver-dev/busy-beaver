import pytest

from busy_beaver.extensions import db as db
from tests._utilities import FactoryManager


@pytest.fixture(name="db", scope="module")
def database(app):
    """Test database."""
    db.app = app
    db.create_all()
    yield db

    db.drop_all()


@pytest.fixture(name="session", scope="function")
def create_sqlalchemy_scoped_session(db):
    """Creates a new database session for each test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})

    session = db.create_scoped_session(options=options)
    db.session = session
    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture(name="factory")
def factory_manager(session):
    yield FactoryManager(session)
