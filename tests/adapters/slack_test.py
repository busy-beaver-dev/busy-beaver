import pytest

from busy_beaver.adapters.slack import SlackAdapter
from busy_beaver.config import SLACK_TOKEN


MODULE_TO_TEST = "busy_beaver.adapters.slack"


@pytest.fixture(scope="module")
def slack():
    return SlackAdapter(SLACK_TOKEN)


@pytest.mark.vcr()
def test_slack_dm(slack: SlackAdapter):
    # Act
    result = slack.dm("test", user_id="U5FTQ3QRZ")

    # Assert
    assert result["ok"] is True
    assert result["message"]["text"] == "test"


@pytest.mark.vcr()
def test_slack_get_channel_info(slack: SlackAdapter):
    # Act
    result = slack.get_channel_info("general")

    # Assert
    assert result.name == "general"
    assert isinstance(result.id, str)
    assert len(result.members) > 0


@pytest.mark.vcr()
def test_slack_get_user_timezone(slack: SlackAdapter):
    # Act
    result = slack.get_user_timezone("U5FTQ3QRZ")

    # Assert
    assert result.tz == "America/Chicago"
    assert result.label == "Central Daylight Time"
    assert result.offset == -18000


@pytest.mark.vcr()
def test_slack_post_ephemeral_message_success(slack: SlackAdapter):
    # Act
    result = slack.post_ephemeral_message(
        "test", channel_id="CEWD83Y74", user_id="U5FTQ3QRZ"
    )

    # Assert
    assert result["ok"] is True


@pytest.mark.vcr()
def test_slack_post_message_success(slack: SlackAdapter):
    # Act
    result = slack.post_message("test", channel="general")

    # Assert
    assert result["ok"] is True
    assert result["message"]["text"] == "test"


@pytest.mark.vcr()
def test_slack_post_message_without_specifying_channel(slack: SlackAdapter):
    with pytest.raises(ValueError):
        slack.post_message(message="test")
