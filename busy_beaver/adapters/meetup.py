from typing import NamedTuple
from meetup.api import Client as MeetupClient
from busy_beaver.exceptions import NoMeetupEventsFound


class EventDetails(NamedTuple):
    name: str
    url: str
    dt: int
    venue: str


class MeetupAdapter:
    """Pull the upcoming events from Meetup and send the message to Slack."""

    def __init__(self, api_key):
        self.meetup_client = MeetupClient(api_key)

    def get_events(self, group_name, count=1):
        events = self.meetup_client.GetEvents(group_urlname=group_name)
        if not events.results:
            raise NoMeetupEventsFound

        upcoming_events = []
        for event in events.results[:count]:
            if "venue" in event:
                venue_name = event["venue"]["name"]
            else:
                venue_name = "TBD"

            upcoming_events.append(
                EventDetails(
                    name=event["name"],
                    url=event["event_url"],
                    dt=int(event["time"] / 1000),
                    venue=venue_name,
                )
            )

        return upcoming_events
