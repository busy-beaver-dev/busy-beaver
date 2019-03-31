from busy_beaver.models import ApiUser, User
import pytest


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
