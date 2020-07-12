import pytest

from busy_beaver.apps.upcoming_events.cli import (
    post_upcoming_events_message_to_slack_cli,
)
from busy_beaver.apps.upcoming_events.upcoming_events import (
    generate_next_event_message,
    generate_upcoming_events_message,
)
from tests._utilities import FakeSlackClient


@pytest.mark.unit
def test_generate_next_event(session, factory):
    group = factory.UpcomingEventsGroup()
    factory.Event.create_batch(size=1, group=group)

    result = generate_next_event_message(group.configuration)

    assert "ChiPy" in result["title"]
    assert "http://meetup.com/_ChiPy_/event/blah" in result["title_link"]
    assert "Braintree" in result["text"]


@pytest.mark.unit
def test_generate_upcoming_events_message(session, factory):
    group = factory.UpcomingEventsGroup()
    factory.Event.create_batch(size=10, group=group)

    result = generate_upcoming_events_message(group.configuration, count=1)

    assert len(result) == 3 + 1 * 3  # sections: 3 in the header, each block is 3


@pytest.fixture
def patched_slack(patcher):
    obj = FakeSlackClient()
    return patcher(
        "busy_beaver.apps.upcoming_events.cli", namespace="SlackClient", replacement=obj
    )


@pytest.mark.integration
def test_cli_post_upcoming_events_message_to_slack(
    mocker, runner, session, factory, patched_slack
):
    # Arrange
    installation = factory.SlackInstallation(workspace_id="T093FC1RC")
    config = factory.UpcomingEventsConfiguration(slack_installation=installation)
    group = factory.UpcomingEventsGroup(meetup_urlname="ChiPy", configuration=config)
    factory.Event.create_batch(size=10, group=group)

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