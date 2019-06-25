"""Project wide pytest plugins / fixtures

References:
    - http://alexmic.net/flask-sqlalchemy-pytest/
    - http://flask.pocoo.org/docs/1.0/testing/
"""

from collections import namedtuple
from datetime import timedelta
import uuid

import pytest
from ._utilities import FactoryManager
from busy_beaver.adapters import KeyValueStoreAdapter
from busy_beaver.extensions import rq as _rq
from busy_beaver.toolbox import utc_now_minus

pytest_plugins = ("tests.fixtures.flask", "tests.fixtures.database")


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": [("authorization", "DUMMY")],
        "filter_query_parameters": ["key"],
    }


@pytest.fixture
def kv_store(session):
    return KeyValueStoreAdapter()


@pytest.fixture(scope="module")
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
def create_fake_background_task():
    """This fixture creates fake background jobs.

    When `.queue` is called on a function decorated with `@rq.job`, it creates a
    background job managed by python-rq and returns an object with job details.

    This fixture creates a Fake that looks like an object created by python-rq. Used
    this fixture to replace functions decorated with `@rq.job` so that we can unit test
    "trigger" functions.

    Unit test trigger functions by ensuring data that should be saved to database
    actually is.
    """
    JobDetails = namedtuple("JobDetails", ["id"])

    class FakeBackgroundTask:
        def __init__(self):
            self.id = str(uuid.uuid4())

        def __repr__(self):
            return f"<FakeBackgroundTask: {self.id}>"

        def queue(self, *args, **kwargs):
            return JobDetails(self.id)

    def _create_fake_background_task():
        return FakeBackgroundTask()

    yield _create_fake_background_task


@pytest.fixture(name="factory")
def factory_manager(session):
    yield FactoryManager(session)
