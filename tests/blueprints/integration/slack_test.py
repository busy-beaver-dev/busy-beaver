import pytest

MODULE_TO_TEST = "busy_beaver.blueprints.integration.slack"


@pytest.fixture
def patcher(monkeypatch):
    """Helper to patch in the correct spot"""

    def _patcher(namespace, replacement_object):
        namespace_to_patch = f"{MODULE_TO_TEST}.{namespace}"
        monkeypatch.setattr(namespace_to_patch, replacement_object)
        return replacement_object

    yield _patcher


@pytest.fixture
def patched_slack(patcher):
    def _wrapper(mock_to_return):
        return patcher("slack", mock_to_return)

    return _wrapper


def test_slack_callback_url_verification(client, session, patched_slack):
    # Arrange
    challenge_code = "test_code"
    data = {"type": "url_verification", "challenge": challenge_code}

    # Act
    resp = client.post("/slack-event-subscription", json=data)

    # Assert
    assert resp.status_code == 200
    assert resp.json == {"challenge": challenge_code}


def test_slack_callback_bot_message_is_ignored(mocker, client, session, patched_slack):
    """Bot get notified of its own DM replies to users... ignore"""
    # Arrange
    slack = patched_slack(mocker.MagicMock())
    # TODO find out how messages are really sent and make these tests a lot more robust
    data = {
        "type": "unknown todo",
        "event": {"type": "message", "subtype": "bot_message"},
    }

    # Act
    resp = client.post("/slack-event-subscription", json=data)

    # Assert
    assert resp.status_code == 200
    assert len(slack.mock_calls) == 0


def test_slack_callback_user_dms_bot_reply(mocker, client, session, patched_slack):
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

    # Act
    resp = client.post("/slack-event-subscription", json=data)

    # Assert
    assert resp.status_code == 200
    assert len(slack.mock_calls) == 1
    args, kwargs = slack.post_message.call_args
    assert kwargs["channel_id"] == channel_id
