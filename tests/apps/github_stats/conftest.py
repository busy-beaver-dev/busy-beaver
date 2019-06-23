import pytest

from busy_beaver.models import GitHubSummaryUser


@pytest.fixture
def create_user(session):
    def _new_user(*, slack_id, github_username):
        new_user = GitHubSummaryUser(slack_id=slack_id, github_username=github_username)
        session.add(new_user)
        session.commit()
        return new_user

    return _new_user
