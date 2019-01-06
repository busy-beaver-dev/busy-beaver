from datetime import timedelta

from busy_beaver.backend import utc_now_minus
from busy_beaver.github_stats import generate_summary
from busy_beaver.models import User

import pytest


@pytest.fixture
def user():
    new_user = User()
    new_user.github_username = "alysivji"
    return new_user


@pytest.mark.smoke
@pytest.mark.vcr()
def test_generate_summary(user):
    generate_summary(user, utc_now_minus(timedelta(days=1)))
    assert True
