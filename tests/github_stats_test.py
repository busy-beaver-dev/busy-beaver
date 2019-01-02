from busy_beaver.github_stats import generate_summary
from busy_beaver.models import User

import pytest


@pytest.fixture
def user():
    new_user = User()
    new_user.github_username = "alysivji"
    return new_user


@pytest.mark.vcr()
def test_generate_summary(user):
    result = generate_summary(user)
    assert "github.com/alysivji" in result
