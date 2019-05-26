from .cards import UpcomingEventList
from busy_beaver import meetup
from busy_beaver.adapters.meetup import EventDetails


def generate_upcoming_events_message(group_name: str, count: int):
    events = meetup.get_events(group_name, count=4)
    return UpcomingEventList("Upcoming ChiPy Events", events).to_dict()


def generate_next_event_message(group_name: str):
    event = meetup.get_events(group_name, count=1)[0]
    return next_event_attachment(event)


def next_event_attachment(event: EventDetails) -> dict:
    """Make a Slack attachment for the event."""
    return {
        "mrkdwn_in": ["text", "pretext"],
        "pretext": "*Next ChiPy Event:*",
        "title": event.name,
        "title_link": event.url,
        "fallback": f"{event.name}: {event.url}",
        "text": f"*<!date^{event.dt}^{{time}} {{date_long}}|no date>* at {event.venue}",
        "color": "#008952",
    }
