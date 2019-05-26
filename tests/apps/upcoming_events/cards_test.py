from busy_beaver.apps.upcoming_events.cards import UpcomingEvent, UpcomingEventList
from busy_beaver.factories.event_details import EventDetailsFactory
from busy_beaver.toolbox.slack_block_kit import Context, Divider, Section


def test_upcoming_event():
    event = EventDetailsFactory()

    result = UpcomingEvent(event)

    assert len(result) == 3
    assert isinstance(result[0], Section)
    assert isinstance(result[1], Context)
    assert isinstance(result[2], Divider)


def test_upcoming_event_to_dict():
    event = EventDetailsFactory()

    result = UpcomingEvent(event).to_dict()

    assert len(result) == 3


def test_upcoming_event_list():
    events = EventDetailsFactory.create_batch(size=5)

    result = UpcomingEventList("Upcoming ChiPy Events", events)

    assert isinstance(result[0], Section)
    assert isinstance(result[1], Divider)
    assert len(result) == 17
