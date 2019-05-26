import pytest
from busy_beaver.factories.event_details import EventDetailsFactory
from busy_beaver.apps.upcoming_events.workflow import (
    generate_next_event_message,
    generate_upcoming_events_message,
)

MODULE_TO_TEST = "busy_beaver.apps.upcoming_events.workflow"


@pytest.fixture
def patched_meetup(mocker, patcher):
    class FakeMeetupClient:
        def __init__(self, *, events):
            self.mock = mocker.MagicMock()
            if events:
                self.events = events

        def get_events(self, *args, **kwargs):
            self.mock(*args, **kwargs)
            return self.events

        def __repr__(self):
            return "<FakeMeetupClient>"

    def _wrapper(*, events=None):
        obj = FakeMeetupClient(events=events)
        return patcher(MODULE_TO_TEST, namespace="meetup", replacement=obj)

    return _wrapper


@pytest.mark.unit
def test_generate_next_event(patched_meetup):
    events = EventDetailsFactory.create_batch(size=1)
    patched_meetup(events=events)

    result = generate_next_event_message("ChiPy")

    assert "ChiPy" in result["title"]
    assert "http://meetup.com/_ChiPy_/event/blah" in result["title_link"]
    assert "Numerator" in result["text"]


@pytest.mark.unit
def test_generate_upcoming_events_message(patched_meetup):
    events = EventDetailsFactory.create_batch(size=1)
    patched_meetup(events=events)

    result = generate_upcoming_events_message("ChiPy", count=1)

    assert len(result) == 5
