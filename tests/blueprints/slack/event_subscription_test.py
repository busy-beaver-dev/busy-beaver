import pytest
from tests.utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.blueprints.slack.event_subscription"


@pytest.fixture
def patched_slack(patcher):
    obj = FakeSlackClient()
    return patcher(MODULE_TO_TEST, namespace="slack", replacement=obj)


@pytest.mark.integration
def test_slack_callback_url_verification(
    client, session, patched_slack, create_slack_headers
):
    # Arrange
    challenge_code = "test_code"
    data = {"type": "url_verification", "challenge": challenge_code}
    headers = create_slack_headers(100_000_000, data)

    # Act
    resp = client.post("/slack/event-subscription", headers=headers, json=data)

    # Assert
    assert resp.status_code == 200
    assert resp.json == {"challenge": challenge_code}


@pytest.mark.integration
def test_slack_callback_bot_message_is_ignored(
    mocker, client, session, patched_slack, create_slack_headers
):
    """Bot get notified of its own DM replies to users... ignore"""
    # Arrange
    data = {
        "type": "unknown todo",
        "event": {"type": "message", "subtype": "bot_message"},
    }
    headers = create_slack_headers(100_000_000, data)

    # Act
    resp = client.post("/slack/event-subscription", headers=headers, json=data)

    # Assert
    assert resp.status_code == 200
    assert len(patched_slack.mock.mock_calls) == 0


@pytest.mark.integration
def test_slack_callback_user_dms_bot_reply(
    mocker, client, session, patched_slack, create_slack_headers
):
    """When user messages bot, reply with help text"""
    # Arrange
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
    resp = client.post("/slack/event-subscription", headers=headers, json=data)

    # Assert
    assert resp.status_code == 200
    assert len(patched_slack.mock.mock_calls) == 1
    args, kwargs = patched_slack.mock.call_args
    assert "/busybeaver help" in args[0]
    assert kwargs["channel_id"] == channel_id
