import pytest
from busy_beaver.factories.event import EventFactory
from busy_beaver.apps.upcoming_events.workflow import (
    generate_next_event_message,
    generate_upcoming_events_message,
)


@pytest.mark.unit
def test_generate_next_event(session):
    events = EventFactory.create_batch(size=1)
    [session.add(event) for event in events]
    session.commit()

    result = generate_next_event_message("ChiPy")

    assert "ChiPy" in result["title"]
    assert "http://meetup.com/_ChiPy_/event/blah" in result["title_link"]
    assert "Numerator" in result["text"]


@pytest.mark.unit
def test_generate_upcoming_events_message(session):
    events = EventFactory.create_batch(size=10)
    [session.add(event) for event in events]
    session.commit()

    result = generate_upcoming_events_message("ChiPy", count=1)

    assert len(result) == 5
