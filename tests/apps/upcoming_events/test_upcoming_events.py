from datetime import datetime, timedelta

import pytest

from busy_beaver.apps.upcoming_events.upcoming_events import (
    generate_next_event_message,
    generate_upcoming_events_message,
)
from tests._utilities import FakeSlackClient


@pytest.mark.unit
def test_generate_next_event(session, factory):
    group = factory.UpcomingEventsGroup()
    factory.Event.create_batch(size=1, group=group)

    result = generate_next_event_message(group.configuration)

    assert "ChiPy" in result["title"]
    assert "http://meetup.com/_ChiPy_/event/blah" in result["title_link"]
    assert "Braintree" in result["text"]


@pytest.mark.unit
def test_generate_upcoming_events_message(session, factory):
    config = factory.UpcomingEventsConfiguration(post_num_events=1)
    group = factory.UpcomingEventsGroup(configuration=config)
    factory.Event.create_batch(size=10, group=group)

    result = generate_upcoming_events_message(group.configuration)

    assert len(result) == 3 + 1 * 3  # sections: 3 in the header, each block is 3


@pytest.mark.unit
def test_events_from_different_group_are_displayed_correct(session, factory):
    """Upcoming Events can come from 2 different groups

    Confirm both events are displayed in the correct order
    """
    # Arrange
    tomorrow = datetime.utcnow() + timedelta(days=1)
    config = factory.UpcomingEventsConfiguration(post_num_events=5)
    group = factory.UpcomingEventsGroup(meetup_urlname="Group 1", configuration=config)
    factory.Event(group=group, name="First event", start_epoch=tomorrow.timestamp())

    next_week = datetime.utcnow() + timedelta(weeks=1)
    group = factory.UpcomingEventsGroup(
        meetup_urlname="Different Group", configuration=config
    )
    factory.Event(group=group, name="Second event", start_epoch=next_week.timestamp())

    # Act
    result = generate_upcoming_events_message(group.configuration)

    # Assert
    first_event = result[3]
    assert "First event" in first_event["text"]["text"]

    second_event = result[6]
    assert "Second event" in second_event["text"]["text"]


@pytest.fixture
def patched_slack(patcher):
    obj = FakeSlackClient()
    return patcher(
        "busy_beaver.apps.upcoming_events.cli", namespace="SlackClient", replacement=obj
    )
