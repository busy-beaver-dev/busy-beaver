from collections import OrderedDict
import json
from urllib.parse import urlencode

import pytest

from busy_beaver.blueprints.integration.slack import (
    command_not_found,
    display_help_text,
    link_github,
    next_event,
    relink_github,
)
from busy_beaver.config import SLACK_SIGNING_SECRET
from busy_beaver.models import User
from busy_beaver.decorators.verification import calculate_signature

MODULE_TO_TEST = "busy_beaver.blueprints.integration.slack"


@pytest.fixture
def add_user(session):
    def _add_user(username):
        user = User(slack_id=username)
        session.add(user)
        session.commit()
        return user

    return _add_user


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


@pytest.mark.integration
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


@pytest.mark.integration
def test_slack_callback_bot_message_is_ignored(
    mocker, client, session, patched_slack, create_slack_headers
):
    """Bot get notified of its own DM replies to users... ignore"""
    # Arrange
    slack = patched_slack(mocker.MagicMock())
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


@pytest.mark.integration
def test_slack_callback_user_dms_bot_reply(
    mocker, client, session, patched_slack, create_slack_headers
):
    """When user messages bot, reply with help text"""
    # Arrange
    slack = patched_slack(mocker.MagicMock())
    channel_id = 5
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
    assert "/busybeaver help" in args[0]
    assert kwargs["channel_id"] == channel_id


###########################
# Slack Slash Command Tests
###########################
@pytest.fixture
def generate_slash_command_request():
    def _generate_data(
        command,
        user_id="U5FRZAD323",
        channel_id="CFLDRNBSDFD",
        team_id="T5GCMNWAFSDFSDF",
    ):
        return {
            "token": "deprecated",
            "team_id": team_id,
            "team_domain": "cant-depend-on-this",
            "channel_id": channel_id,
            "channel_name": "cant-depend-on-this",
            "user_id": user_id,
            "user_name": "cant-depend-on-this",
            "command": "/busybeaver",
            "text": command,
            "response_url": "https://hooks.slack.com/commands/T5GCMNW/639192748/39",
            "trigger_id": "639684516021.186015429778.0a18640db7b29f98749b62f6e824fe30",
        }

    return _generate_data


@pytest.mark.integration
def test_slack_command_valid_command(
    client, create_slack_headers, generate_slash_command_request
):
    data = generate_slash_command_request("help")
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack-slash-commands", headers=headers, data=data)

    assert response.status_code == 200
    assert "/busybeaver help" in response.json["text"].lower()


@pytest.mark.integration
def test_slack_command_invalid_command(
    client, create_slack_headers, generate_slash_command_request
):
    data = generate_slash_command_request("non-existent")
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack-slash-commands", headers=headers, data=data)

    assert response.status_code == 200
    assert "command not found" in response.json["text"].lower()


@pytest.mark.integration
def test_slack_command_empty_command(
    client, create_slack_headers, generate_slash_command_request
):
    data = generate_slash_command_request(command="")
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack-slash-commands", headers=headers, data=data)

    assert response.status_code == 200
    assert "/busybeaver help" in response.json["text"].lower()


#########################
# Upcoming Event Schedule
#########################
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


@pytest.mark.unit
def test_command_next_event(generate_slash_command_request, patched_meetup):
    data = generate_slash_command_request("next")
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

    result = next_event(**data)

    slack_response = result.json["attachments"][0]
    assert "ChiPy" in slack_response["title"]
    assert "http://meetup.com/_ChiPy_/event/blah" in slack_response["title_link"]
    assert "Numerator" in slack_response["text"]


@pytest.mark.unit
def test_command_next_event_location_not_set(
    generate_slash_command_request, patched_meetup
):
    data = generate_slash_command_request("next")
    patched_meetup(
        events=[
            {
                "name": "ChiPy",
                "event_url": "http://meetup.com/_ChiPy_/event/blah",
                "time": 1_557_959_400_000,
            }
        ]
    )

    result = next_event(**data)

    slack_response = result.json["attachments"][0]
    assert "ChiPy" in slack_response["title"]
    assert "http://meetup.com/_ChiPy_/event/blah" in slack_response["title_link"]
    assert "TBD" in slack_response["text"]


##########################################
# Associate GitHub account with Slack user
##########################################
@pytest.mark.unit
def test_connect_command_new_user(session, generate_slash_command_request):
    data = generate_slash_command_request("connect", user_id="new_user")

    result = link_github(**data)

    # TODO this is painful, think of a better way of testing these kinds of messages
    # maybe a test helper?
    assert (
        "Associate GitHub Profile"
        in result.json["attachments"][0]["actions"][0]["text"]
    )


@pytest.mark.unit
def test_connect_command_existing_user(add_user, generate_slash_command_request):
    add_user(username="existing_user")
    data = generate_slash_command_request("connect", user_id="existing_user")

    result = link_github(**data)

    assert "/busybeaver reconnect" in result.json["text"]


@pytest.mark.unit
def test_reconnect_command_new_user(session, generate_slash_command_request):
    data = generate_slash_command_request("reconnect", user_id="new_user")

    result = relink_github(**data)

    assert "/busybeaver connect" in result.json["text"]


@pytest.mark.unit
def test_reconnect_command_existing_user(generate_slash_command_request, add_user):
    add_user(username="existing_user")
    data = generate_slash_command_request("reconnect", user_id="existing_user")

    result = relink_github(**data)

    assert (
        "Associate GitHub Profile"
        in result.json["attachments"][0]["actions"][0]["text"]
    )


########################
# Miscellaneous Commands
########################
@pytest.mark.unit
def test_command_help(generate_slash_command_request):
    data = generate_slash_command_request("help")

    result = display_help_text(**data)

    assert "/busybeaver help" in result.json["text"]


@pytest.mark.unit
def test_command_not_found(generate_slash_command_request):
    data = generate_slash_command_request(command="blah")

    result = command_not_found(**data)

    assert "/busybeaver help" in result.json["text"]
