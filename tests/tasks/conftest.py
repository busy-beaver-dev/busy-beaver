import pytest

from busy_beaver.models import User


@pytest.fixture
def create_user(session):
    def _new_user(*, slack_id, github_username):
        new_user = User(slack_id=slack_id, github_username=github_username)
        session.add(new_user)
        session.commit()
        return new_user

    return _new_user


@pytest.fixture
def fake_slack_client(mocker):
    class FakeSlackClient:
        def __init__(self, *, channel_info=None):
            self.mock = mocker.MagicMock()
            if channel_info:
                self.channel_info = channel_info

        def get_channel_info(self, *args, **kwargs):
            self.mock(*args, **kwargs)
            return self.channel_info

        def post_message(self, *args, **kwargs):
            self.mock(*args, **kwargs)
            return

        def __repr__(self):
            return "<FakeSlackClient>"

    return FakeSlackClient
