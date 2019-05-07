from unittest import mock

from meetup.api import Client as MeetupClient

from busy_beaver.blueprints.tasks.slack import (
    NextMeetupCommandHandler,
    dispatch_slash_command,
)


def test_slash_command_dispatch_empty():
    """Empty command text is ignored."""
    command_text = ""
    channel = "general"

    status = dispatch_slash_command(command_text, channel)

    assert not status


def test_invalid_slash_command():
    """An invalid slash command is ignored."""
    command_text = "bogus command"
    channel = "general"

    status = dispatch_slash_command(command_text, channel)

    assert not status


@mock.patch.object(NextMeetupCommandHandler, "handle")
def test_next_slash_command(handle):
    """The `next` command is dispatched successfully."""
    command_text = "next"
    channel = "general"

    status = dispatch_slash_command(command_text, channel)

    assert status
    assert handle.called


@mock.patch("busy_beaver.blueprints.tasks.slack.slack")
def test_no_events(slack):
    """No events in Meetup will trigger no message in Slack."""
    mock_client = mock.MagicMock()
    mock_events = mock.MagicMock()
    mock_events.results = []
    mock_client.GetEvents.return_value = mock_events
    meetup_handler = NextMeetupCommandHandler(mock_client)
    command_text = "next"
    channel = "general"

    meetup_handler.handle(command_text, channel)

    assert not slack.post_message.called


@mock.patch("busy_beaver.blueprints.tasks.slack.slack")
def test_send_slack_message_with_event(slack):
    """A Slack message is sent out when there is an upcoming event."""
    mock_client = mock.MagicMock()
    mock_events = mock.MagicMock()
    mock_events.results = [
        {"name": "Test Event", "event_url": "https://testserver", "time": 1557258100000}
    ]
    mock_client.GetEvents.return_value = mock_events
    meetup_handler = NextMeetupCommandHandler(mock_client)
    command_text = "next"
    channel = "general"

    meetup_handler.handle(command_text, channel)

    assert slack.post_message.called
