from meetup.api import Client as MeetupClient

from busy_beaver.exceptions import NoMeetupEventsFound


class MeetupAdapter:
    """Pull the upcoming events from Meetup and send the message to Slack."""

    def __init__(self, api_key):
        self.meetup_client = MeetupClient(api_key)

    def get_events(self, group_name, count=1):
        events = self.meetup_client.GetEvents(group_urlname=group_name)
        if not events.results:
            raise NoMeetupEventsFound
        return events.results[:count]
