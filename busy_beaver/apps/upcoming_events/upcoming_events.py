import time

from busy_beaver.apps.upcoming_events.cards import UpcomingEventList
from busy_beaver.common.wrappers.meetup import EventDetails
from busy_beaver.models import Event, UpcomingEventsConfiguration


def generate_upcoming_events_message(config: UpcomingEventsConfiguration):
    # if 0 upcoming events
    events = _fetch_future_events_from_database(config, count=config.post_num_events)
    image_url = config.slack_installation.workspace_logo_url
    return UpcomingEventList(events, image_url).to_dict()


def generate_next_event_message(config: UpcomingEventsConfiguration):
    event = _fetch_future_events_from_database(config, count=1)
    if event:
        return _next_event_attachment(event)
    else:
        return {
            "mrkdwn_in": ["text", "pretext"],
            "pretext": "*Next Event:*",
            "text": "No upcoming events scheduled",
            "color": "#008952",
        }


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
    text = (
        f"*<!date^{event.start_epoch}^{{time}} "
        f"{{date_long}}|no date>* at {event.venue}"
    )
    return {
        "mrkdwn_in": ["text", "pretext"],
        "pretext": "*Next Event:*",
        "title": event.name,
        "title_link": event.url,
        "fallback": f"{event.name}: {event.url}",
        "text": text,
        "color": "#008952",
    }
