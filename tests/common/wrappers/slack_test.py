import pytest

from busy_beaver.apps.slack_integration.blocks import AppHome
from busy_beaver.common.wrappers.slack import SlackClient
from busy_beaver.config import SLACK_TOKEN

MODULE_TO_TEST = "busy_beaver.common.wrappers.slack"


@pytest.fixture(scope="module")
def slack():
    return SlackClient(SLACK_TOKEN)


@pytest.mark.vcr()
def test_slack_dm(slack: SlackClient):
    # Act
    result = slack.dm("test", user_id="U5FTQ3QRZ")

    # Assert
    assert result["ok"] is True
    assert result["message"]["text"] == "test"


@pytest.mark.vcr()
def test_slack_get_channel_members(slack: SlackClient):
    members = slack.get_channel_members("C5GQNTS07")
    assert len(members) > 0


@pytest.mark.vcr()
def test_slack_get_channel_members__channel_does_not_exist(slack: SlackClient):
    with pytest.raises(ValueError):
        slack.get_channel_members("channel-does-not-exist")


@pytest.mark.vcr()
def test_slack_get_user_timezone(slack: SlackClient):
    # Act
    result = slack.get_user_timezone("U5FTQ3QRZ")

    # Assert
    assert result.tz == "America/Chicago"
    assert result.label == "Central Daylight Time"
    assert result.offset == -18000


@pytest.mark.vcr()
def test_slack_post_ephemeral_message_success(slack: SlackClient):
    # Act
    result = slack.post_ephemeral_message(
        "test", channel="CEWD83Y74", user_id="U5FTQ3QRZ"
    )

    # Assert
    assert result["ok"] is True


@pytest.mark.vcr()
def test_slack_post_message_success(slack: SlackClient):
    # Act
    result = slack.post_message("test", channel="general")

    # Assert
    assert result["ok"] is True
    assert result["message"]["text"] == "test"


@pytest.mark.vcr()
def test_slack_post_message_without_specifying_channel(slack: SlackClient):
    with pytest.raises(ValueError):
        slack.post_message(message="test")


@pytest.mark.vcr()
def test_slack_display_app_home(slack: SlackClient):
    result = slack.display_app_home("U5FTQ3QRZ", view=AppHome().to_dict())

    assert result.status_code == 200
    assert result["ok"] is True
    assert result["view"]
