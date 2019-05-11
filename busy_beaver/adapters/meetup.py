from meetup.api import Client as MeetupClient

from busy_beaver import config
from busy_beaver.exceptions import NoMeetupEventsFound


class MeetupAdapter:
    """Pull the upcoming events from Meetup and send the message to Slack."""

    def __init__(self, api_key):
        self.meetup_client = MeetupClient(api_key)

    def get_events(self, num=1):
        events = self.meetup_client.GetEvents(group_urlname=config.MEETUP_GROUP_NAME)
        if not events.results:
            raise NoMeetupEventsFound
        return events.results[:num]
