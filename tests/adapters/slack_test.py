import pytest

from busy_beaver.common.wrappers.slack import SlackClient
from busy_beaver.config import SLACK_TOKEN
from busy_beaver.apps.slack_integration.blocks import AppHome


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
def test_slack_get_channel_info(slack: SlackClient):
    # Act
    result = slack.get_channel_info("C5GQNTS07")

    # Assert
    assert result.name == "C5GQNTS07"
    assert len(result.members) > 0


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
def test_slack_get_channel_list(slack: SlackClient):
    result = slack.get_channel_list()

    assert result["ok"] is True
    channel_info = result["channels"]
    if channel_info:
        assert "members" not in channel_info[0]


@pytest.mark.vcr()
def test_slack_get_channel_list_with_members(slack: SlackClient):
    result = slack.get_channel_list(include_members=True)

    assert result["ok"] is True
    channel_info = result["channels"]
    if channel_info:
        assert "members" in channel_info[0]


@pytest.mark.vcr()
def test_slack_display_app_home(slack: SlackClient):
    result = slack.display_app_home("U5FTQ3QRZ", view=AppHome().to_dict())

    assert result.status_code == 200
    assert result["ok"] is True
    assert result["view"]
