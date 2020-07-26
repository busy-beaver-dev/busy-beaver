import time

from busy_beaver.apps.upcoming_events.cards import UpcomingEventList
from busy_beaver.common.wrappers.meetup import EventDetails
from busy_beaver.models import Event, UpcomingEventsConfiguration


def generate_upcoming_events_message(config: UpcomingEventsConfiguration, count: int):
    events = _fetch_future_events_from_database(config, count)
    # TODO: for multi-tenant we will need to use group_name to look up url
    image_url = "https://www.chipy.org/static/img/chipmunk.1927e65c68a7.png"
    return UpcomingEventList(events, image_url).to_dict()


def generate_next_event_message(config: UpcomingEventsConfiguration):
    event = _fetch_future_events_from_database(config, count=1)[0]
    return _next_event_attachment(event)


def _fetch_future_events_from_database(config, count):
    current_epoch_time = int(time.time())
    groups = [group.id for group in config.groups]
    upcoming_events_in_db = (
        Event.query.filter(Event.group_id.in_(groups))
        .filter(Event.start_epoch > current_epoch_time)
        .order_by(Event.start_epoch)
        .limit(count)
    )
    return [EventDetails.from_event_model(model) for model in upcoming_events_in_db]


def _next_event_attachment(event: EventDetails) -> dict:
    """Make a Slack attachment for the event."""
    return {
        "mrkdwn_in": ["text", "pretext"],
        "pretext": "*Next Event:*",
        "title": event.name,
        "title_link": event.url,
        "fallback": f"{event.name}: {event.url}",
        "text": f"*<!date^{event.start_epoch}^{{time}} {{date_long}}|no date>* at {event.venue}",
        "color": "#008952",
    }
