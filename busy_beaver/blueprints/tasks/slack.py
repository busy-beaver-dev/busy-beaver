from meetup.api import Client as MeetupClient

from busy_beaver import config, slack
from busy_beaver.extensions import rq


class NextMeetupCommandHandler:
    """Pull the upcoming events from Meetup and send the message to Slack."""

    def __init__(self, meetup_client=None):
        if meetup_client is None:
            self.meetup_client = MeetupClient(config.MEETUP_API_KEY)
        else:
            self.meetup_client = meetup_client

    def handle(self, command_text: str, channel: str) -> None:
        events = self.meetup_client.GetEvents(group_urlname=config.MEETUP_GROUP_NAME)
        if not events.results:
            return

        attachment = self.make_slack_event_attachment(events.results[0])
        slack.post_message(attachments=[attachment], channel=channel)

    def make_slack_event_attachment(self, event: dict) -> dict:
        """Make a Slack attachment for the event."""
        if "venue" in event:
            venue_name = event["venue"]["name"]
        else:
            venue_name = "TBD"

        return {
            "mrkdwn_in": ["text", "pretext"],
            "pretext": "*Next Meetup:*",
            "title": event["name"],
            "title_link": event["event_url"],
            "fallback": "{}: {}".format(event["name"], event["event_url"]),
            "text": "*<!date^{}^{{time}} {{date_long}}|no date>* at {}".format(
                int(event["time"] / 1000), venue_name
            ),
            "color": "#008952",
        }


SLASH_COMMANDS = {"next": NextMeetupCommandHandler}


@rq.job
def dispatch_slash_command(command_text: str, channel: str) -> bool:
    """Dispatch and take action to slash command (e.g., /bb next) from Slack."""
    command_parts = command_text.split()
    if not command_parts:
        return False

    command_handler_cls = SLASH_COMMANDS.get(command_parts[0])
    if not command_handler_cls:
        return False

    command_handler_cls().handle(command_text, channel)
    return True
