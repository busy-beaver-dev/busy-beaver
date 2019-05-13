from collections import OrderedDict
import json
from urllib.parse import urlencode

import pytest

from busy_beaver.blueprints.integration.slack import (
    ACCOUNT_ALREADY_ASSOCIATED,
    UNKNOWN_COMMAND,
    VERIFY_ACCOUNT,
    reply_to_user_with_github_login_link,
)
from busy_beaver.config import SLACK_SIGNING_SECRET
from busy_beaver.models import User
from busy_beaver.decorators.verification import calculate_signature

MODULE_TO_TEST = "busy_beaver.blueprints.integration.slack"


################################
# Slack Event Subscription Tests
################################
@pytest.fixture
def patched_slack(patcher):
    def _wrapper(replacement):
        return patcher(MODULE_TO_TEST, namespace="slack", replacement=replacement)

    return _wrapper


@pytest.fixture
def create_slack_headers():
    """Dictionary get sorted when we retrieve the body, account for this"""

    def sort_dict(original_dict):
        res = OrderedDict()
        for k, v in sorted(original_dict.items()):
            if isinstance(v, dict):
                res[k] = dict(sort_dict(v))
            else:
                res[k] = v
        return dict(res)

    def wrapper(timestamp, data, is_json_data=True):
        if is_json_data:
            request_body = json.dumps(sort_dict(data)).encode("utf-8")
        else:
            request_body = urlencode(data).encode("utf-8")
        sig = calculate_signature(SLACK_SIGNING_SECRET, timestamp, request_body)
        return {"X-Slack-Request-Timestamp": timestamp, "X-Slack-Signature": sig}

    return wrapper


def test_slack_callback_url_verification(
    client, session, patched_slack, create_slack_headers
):
    # Arrange
    challenge_code = "test_code"
    data = {"type": "url_verification", "challenge": challenge_code}
    headers = create_slack_headers(100_000_000, data)

    # Act
    resp = client.post("/slack-event-subscription", headers=headers, json=data)

    # Assert
    assert resp.status_code == 200
    assert resp.json == {"challenge": challenge_code}


def test_slack_callback_bot_message_is_ignored(
    mocker, client, session, patched_slack, create_slack_headers
):
    """Bot get notified of its own DM replies to users... ignore"""
    # Arrange
    slack = patched_slack(mocker.MagicMock())
    # TODO find out how messages are really sent and make these tests a lot more robust
    data = {
        "type": "unknown todo",
        "event": {"type": "message", "subtype": "bot_message"},
    }
    headers = create_slack_headers(100_000_000, data)

    # Act
    resp = client.post("/slack-event-subscription", headers=headers, json=data)

    # Assert
    assert resp.status_code == 200
    assert len(slack.mock_calls) == 0


def test_slack_callback_user_dms_bot_reply(
    mocker, client, session, patched_slack, create_slack_headers
):
    """Bot get notified of its own DM replies to users... ignore"""
    # Arrange
    slack = patched_slack(mocker.MagicMock())
    channel_id = 5
    # TODO find out how messages are really sent and make these tests a lot more robust
    data = {
        "type": "unknown todo",
        "event": {
            "type": "message",
            "subtype": "not bot_message",
            "channel_type": "im",
            "text": "random",
            "user": "random_user",
            "channel": channel_id,
        },
    }
    headers = create_slack_headers(100_000_000, data)

    # Act
    resp = client.post("/slack-event-subscription", headers=headers, json=data)

    # Assert
    assert resp.status_code == 200
    assert len(slack.mock_calls) == 1
    args, kwargs = slack.post_message.call_args
    assert kwargs["channel_id"] == channel_id


@pytest.fixture
def create_slack_message():
    def _create_slack_message_dict(*, text, user="test_user"):
        return {
            "type": "message",
            "subtype": "not bot_message",  # TODO, what does it really look like
            "channel_type": "im",
            "text": text,
            "user": user,
            "channel": "test_channel",
        }

    return _create_slack_message_dict


def test_reply_unknown_command(mocker, session, patched_slack, create_slack_message):
    # Arrange
    slack = patched_slack(mocker.MagicMock())
    message = create_slack_message(text="hi")

    # Act
    reply_to_user_with_github_login_link(message)

    # Assert
    assert len(slack.mock_calls) == 1
    args, kwargs = slack.post_message.call_args
    assert UNKNOWN_COMMAND in args


def test_reply_new_account(mocker, session, patched_slack, create_slack_message):
    # Arrange
    slack = patched_slack(mocker.MagicMock())
    message = create_slack_message(text="connect")

    # Act
    reply_to_user_with_github_login_link(message)

    # Assert
    assert len(slack.mock_calls) == 1
    args, kwargs = slack.post_message.call_args
    assert VERIFY_ACCOUNT in args


def test_reply_existing_account(mocker, session, patched_slack, create_slack_message):
    # Arrange
    username = "test_user"
    user = User(slack_id=username)
    session.add(user)
    session.commit()

    message = create_slack_message(text="connect", user=username)
    slack = patched_slack(mocker.MagicMock())

    # Act
    reply_to_user_with_github_login_link(message)

    # Assert
    assert len(slack.mock_calls) == 1
    args, kwargs = slack.post_message.call_args
    assert ACCOUNT_ALREADY_ASSOCIATED in args


def test_reply_existing_account_reconnect(
    mocker, session, patched_slack, create_slack_message
):
    # Arrange
    username = "test_user"
    user = User(slack_id=username)
    session.add(user)
    session.commit()

    message = create_slack_message(text="reconnect", user=username)
    slack = patched_slack(mocker.MagicMock())

    # Act
    reply_to_user_with_github_login_link(message)

    # Assert
    assert len(slack.mock_calls) == 1
    args, kwargs = slack.post_message.call_args
    assert VERIFY_ACCOUNT in args


###########################
# Slack Slash Command Tests
###########################
@pytest.fixture
def patched_meetup(mocker, patcher):
    class FakeMeetupClient:
        def __init__(self, *, events):
            self.mock = mocker.MagicMock()
            if events:
                self.events = events

        def get_events(self, *args, **kwargs):
            self.mock(*args, **kwargs)
            return self.events

        def __repr__(self):
            return "<FakeMeetupClient>"

    def _wrapper(*, events=None):
        obj = FakeMeetupClient(events=events)
        return patcher(MODULE_TO_TEST, namespace="meetup", replacement=obj)

    return _wrapper


def test_slack_command_next_event(client, create_slack_headers, patched_meetup):
    data = {"command": "busybeaver", "text": "next with junk"}
    headers = create_slack_headers(100_000_000, data, is_json_data=False)
    patched_meetup(
        events=[
            {
                "venue": {"name": "Numerator"},
                "name": "ChiPy",
                "event_url": "http://meetup.com/_ChiPy_/event/blah",
                "time": 1_557_959_400_000,
            }
        ]
    )

    response = client.post("/slack-slash-commands", headers=headers, data=data)

    assert response.status_code == 200
    slack_response = response.json["attachments"][0]
    assert "ChiPy" in slack_response["title"]
    assert "http://meetup.com/_ChiPy_/event/blah" in slack_response["title_link"]


def test_slack_command_invalid_command(client, create_slack_headers, patched_meetup):
    data = {"command": "busybeaver", "text": "non-existent"}
    headers = create_slack_headers(100_000_000, data, is_json_data=False)
    patched_meetup(
        events=[
            {
                "venue": {"name": "Numerator"},
                "name": "ChiPy",
                "event_url": "http://meetup.com/_ChiPy_/event/blah",
                "time": 1_557_959_400_000,
            }
        ]
    )

    response = client.post("/slack-slash-commands", headers=headers, data=data)

    assert response.status_code == 200
    assert "command not found" in response.json.lower()
