from typing import List, NamedTuple
from meetup.api import Client as MeetupClient

from busy_beaver.exceptions import NoMeetupEventsFound
from busy_beaver.models import Event


class EventDetails(NamedTuple):
    id: str
    name: str
    url: str
    venue: str
    dt: int  # utc epoch

    def create_event_record(self) -> Event:
        return Event(
            remote_id=self.id,
            name=self.name,
            url=self.url,
            venue=self.venue,
            utc_epoch=self.dt,
        )


class MeetupAdapter:
    """Pull the upcoming events from Meetup and send the message to Slack."""

    def __init__(self, api_key):
        self.meetup_client = MeetupClient(api_key)

    def get_events(self, group_name: str, count: int = 1) -> List[EventDetails]:
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
                    id=event["id"],
                    name=event["name"],
                    url=event["event_url"],
                    venue=venue_name,
                    dt=int(event["time"] / 1000),
                )
            )

        return upcoming_events
