import pytest
from busy_beaver.adapters import MeetupAdapter
from busy_beaver.config import MEETUP_API_KEY


@pytest.fixture
def meetup_client():
    return MeetupAdapter(MEETUP_API_KEY)


@pytest.mark.vcr()
def test_meetup_adapter_get_events(meetup_client):
    events = meetup_client.get_events("_ChiPy_", count=1)
    assert len(events) == 1
