import pytest
from tests._utilities import FakeSlackClient

from busy_beaver.apps.upcoming_events.workflow import (
    generate_next_event_message,
    generate_upcoming_events_message,
    post_upcoming_events_message_to_slack,
    post_upcoming_events_message_to_slack_cli,
)

MODULE_TO_TEST = "busy_beaver.apps.upcoming_events.workflow"


@pytest.mark.unit
def test_generate_next_event(session, factory):
    factory.Event.create_batch(size=1)

    result = generate_next_event_message("ChiPy")

    assert "ChiPy" in result["title"]
    assert "http://meetup.com/_ChiPy_/event/blah" in result["title_link"]
    assert "Numerator" in result["text"]


@pytest.mark.unit
def test_generate_upcoming_events_message(session, factory):
    factory.Event.create_batch(size=10)

    result = generate_upcoming_events_message("ChiPy", count=1)

    assert len(result) == 3 + 1 * 3  # sections: 3 in the header, each block is 3


@pytest.fixture
def patched_slack(patcher):
    obj = FakeSlackClient()
    return patcher(MODULE_TO_TEST, namespace="SlackClient", replacement=obj)


@pytest.mark.unit
def test_post_upcoming_events_message_to_slack(mocker, session, factory, patched_slack):
    # Arrange
    factory.SlackInstallation(workspace_id="T093FC1RC")
    factory.Event.create_batch(size=10)

    # Act
    post_upcoming_events_message_to_slack("announcements", "ChiPy", count=4)

    # Assert
    post_message_args = patched_slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert len(kwargs["blocks"]) == 15  # sections: 3 in the header, each block is 3


@pytest.mark.integration
def test_cli_post_upcoming_events_message_to_slack(
    mocker, runner, session, factory, patched_slack
):
    # Arrange
    factory.SlackInstallation(workspace_id="T093FC1RC")
    factory.Event.create_batch(size=10)

    # Act
    runner.invoke(
        post_upcoming_events_message_to_slack_cli,
        [
            "--workspace",
            "T093FC1RC",
            "--channel",
            "announcements",
            "--group_name",
            "ChiPy",
            "--count",
            4,
        ],
    )

    # Assert
    post_message_args = patched_slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert len(kwargs["blocks"]) == 15  # sections: 3 in the header, each block is 3
