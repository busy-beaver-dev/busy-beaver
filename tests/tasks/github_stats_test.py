from datetime import timedelta

from busy_beaver.models import User
from busy_beaver.tasks.github_stats.summary import generate_summary
from busy_beaver.toolbox import utc_now_minus

import pytest


@pytest.fixture
def create_user():
    def _new_user(github_username):
        new_user = User()
        new_user.github_username = github_username
        return new_user

    return _new_user


# TODO make freze_time into a test helper that pulls from the cassette directly
@pytest.mark.vcr()
@pytest.mark.freeze_time("2019-01-05")
def test_generate_summary(create_user):
    user = create_user("alysivji")

    assert "alysivji" in generate_summary(user, utc_now_minus(timedelta(days=1)))
