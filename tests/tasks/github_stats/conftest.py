from collections import namedtuple
import uuid

import pytest

from busy_beaver.models import ApiUser, User


@pytest.fixture
def create_user():
    def _new_user(github_username):
        new_user = User()
        new_user.github_username = github_username
        return new_user

    return _new_user


@pytest.fixture
def create_api_user():
    def _new_api_user(username, *, role="user"):
        new_api_user = ApiUser(username="test_user", token="abcd", role=role)
        return new_api_user

    return _new_api_user


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
