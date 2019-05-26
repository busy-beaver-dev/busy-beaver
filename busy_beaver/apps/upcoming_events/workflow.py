import time
from busy_beaver.apps.upcoming_events.cards import UpcomingEventList
from busy_beaver.adapters.meetup import EventDetails
from busy_beaver.models import Event


def generate_upcoming_events_message(group_name: str, count: int):
    events = _fetch_future_events_from_database(group_name, count)
    return UpcomingEventList("Upcoming ChiPy Events", events).to_dict()


def generate_next_event_message(group_name: str):
    event = _fetch_future_events_from_database(group_name, count=1)[0]
    return _next_event_attachment(event)


def _fetch_future_events_from_database(group_name, count):
    # TODO: for multi-tenant we will need use group_name in query
    current_epoch_time = int(time.time())
    upcoming_events_in_db = (
        Event.query.filter(Event.utc_epoch > current_epoch_time)
        .order_by(Event.utc_epoch)
        .limit(count)
    )
    return [EventDetails.from_event_model(model) for model in upcoming_events_in_db]


def _next_event_attachment(event: EventDetails) -> dict:
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
