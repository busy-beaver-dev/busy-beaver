from busy_beaver.models import User
import pytest


@pytest.fixture
def create_user():
    def _new_user(github_username):
        new_user = User()
        new_user.github_username = github_username
        return new_user

    return _new_user
