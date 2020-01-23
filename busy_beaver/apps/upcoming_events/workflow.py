import time

from busy_beaver.apps.upcoming_events.cards import UpcomingEventList
from busy_beaver.adapters.meetup import EventDetails
from busy_beaver.clients import chipy_slack
from busy_beaver.models import Event


def generate_upcoming_events_message(group_name: str, count: int):
    events = _fetch_future_events_from_database(group_name, count)
    # TODO: for multi-tenant we will need to use group_name to look up url
    image_url = "https://www.chipy.org/static/img/chipmunk.1927e65c68a7.png"
    return UpcomingEventList(events, group_name, image_url).to_dict()


def generate_next_event_message(group_name: str):
    event = _fetch_future_events_from_database(group_name, count=1)[0]
    return _next_event_attachment(event)


def post_upcoming_events_message_to_slack(channel: str, group_name: str, count: int):
    blocks = generate_upcoming_events_message(group_name, count)
    chipy_slack.post_message(blocks=blocks, channel=channel)


def _fetch_future_events_from_database(group_name, count):
    # TODO: for multi-tenant we will need use group_name in query
    current_epoch_time = int(time.time())
    upcoming_events_in_db = (
        Event.query.filter(Event.start_epoch > current_epoch_time)
        .order_by(Event.start_epoch)
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
        "text": f"*<!date^{event.start_epoch}^{{time}} {{date_long}}|no date>* at {event.venue}",
        "color": "#008952",
    }
