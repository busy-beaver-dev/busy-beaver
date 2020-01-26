import uuid

import pytest

from busy_beaver.common.wrappers.meetup import MeetupClient, EventDetails
from busy_beaver.common.wrappers.requests_client import Response
from busy_beaver.config import MEETUP_API_KEY
from busy_beaver.exceptions import NoMeetupEventsFound

MODULE_TO_TEST = "busy_beaver.common.wrappers.meetup"


@pytest.fixture
def meetup_client():
    return MeetupClient(MEETUP_API_KEY)


@pytest.mark.vcr()
@pytest.mark.integration
def test_meetup_get_events(meetup_client):
    events = meetup_client.get_events("_ChiPy_", count=2)
    assert len(events) == 2

    event = events[0]
    assert "ChiPy __main__ Meeting" in event.name
    assert "ActiveCampaign" in event.venue


@pytest.fixture
def patched_requests_client(mocker, patcher):
    class FakeRequestsClient:
        def __init__(self, *, events=None):
            self.mock = mocker.MagicMock()
            self.events = events if events else []

        def __call__(self, *args, **kwargs):
            # We are replacing with a class that is initialized
            return self

        def get(self, *args, **kwargs):
            self.mock(*args, **kwargs)
            return Response(status_code=200, headers={}, json=self.events)

        def __repr__(self):
            return "<FakeRequestsClient>"

    def _wrapper(*, events=None):
        obj = FakeRequestsClient(events=events)
        return patcher(MODULE_TO_TEST, namespace="RequestsClient", replacement=obj)

    return _wrapper


@pytest.mark.unit
def test_venue_not_specified_returns_tbd(patched_requests_client):
    # Arrange
    remote_id = str(uuid.uuid4())
    patched_requests_client(
        events=[
            {
                "id": remote_id,
                "name": "ChiPy",
                "link": "http://meetup.com/_ChiPy_/event/blah",
                "time": 1_557_959_400_000,
                "duration": 1_557_959_400_000 + 60 * 60 * 2,
            }
        ]
    )

    # Act
    events = MeetupClient("API_KEY").get_events("ChiPy", count=1)

    # Assert
    event = events[0]
    assert "ChiPy" in event.name
    assert "http://meetup.com/_ChiPy_/event/blah" in event.url
    assert "TBD" in event.venue
    assert event.id == remote_id


@pytest.mark.unit
def test_no_events_found_raises_exception(patched_requests_client):
    patched_requests_client(events=[])

    with pytest.raises(NoMeetupEventsFound):
        MeetupClient("API_KEY").get_events("ChiPy", count=10)


@pytest.mark.integration
def test_event_details_creating_event_objects(factory):
    # Arrange
    event = factory.Event()

    # Act
    event_details = EventDetails.from_event_model(event)
    created_event = event_details.create_event_record()

    # Assert
    assert event.name == created_event.name
    assert event.start_epoch == created_event.start_epoch
    assert event.venue == created_event.venue


@pytest.mark.unit
def test_event_details_creating_event_object_from_unallowable_type():
    with pytest.raises(ValueError):
        EventDetails.from_event_model({})
