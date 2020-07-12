import pytest

from busy_beaver.apps.upcoming_events.cli import sync_events_database_cli
from busy_beaver.apps.upcoming_events.sync_database import (
    classify_transaction_type,
    sync_database_with_fetched_events,
)
from busy_beaver.models import Event
from tests._utilities import FakeMeetupAdapter

MODULE_TO_TEST = "busy_beaver.apps.upcoming_events.sync_database"


@pytest.fixture
def patched_meetup(patcher):
    def _wrapper(events):
        fake_meetup = FakeMeetupAdapter(events)
        patcher(MODULE_TO_TEST, namespace="meetup", replacement=fake_meetup)

    return _wrapper


@pytest.mark.integration
def test_add_all_events_to_database(session, factory, patched_meetup):
    """
    GIVEN: Empty database
    WHEN: add_events_to_database is called
    THEN: add all events to database
    """
    # Arrange
    group = factory.UpcomingEventsGroup()
    events = factory.EventDetails.create_batch(size=20)
    patched_meetup(events=events)

    # Act
    sync_database_with_fetched_events(group)

    # Assert
    all_events_in_database = Event.query.all()
    assert len(all_events_in_database) == len(events)


@pytest.mark.integration
def test_update_all_events_in_database(session, factory, patched_meetup):
    """
    GIVEN: table contains upcoming events, adapter has same events with updated details
    WHEN: add_events_to_database is called
    THEN: update event information in database
    """
    # Arrange
    group = factory.UpcomingEventsGroup()
    num_events = 20
    database_events = factory.Event.create_batch(size=num_events, group=group)

    fetched_events = []
    for event in database_events:
        fetched_events.append(factory.EventDetails(id=event.remote_id, venue="TBD"))
    patched_meetup(events=fetched_events)

    # Act
    sync_database_with_fetched_events(group)

    # Assert
    all_database_events = Event.query.all()
    assert len(all_database_events) == num_events
    for event in all_database_events:
        assert event.venue == "TBD"


@pytest.mark.integration
def test_delete_all_events_in_database(session, factory, patched_meetup):
    """
    GIVEN: table contains upcoming events, adapter has no events
    WHEN: add_events_to_database is called
    THEN: all events are removed fromd atabase
    """
    # Arrange
    group = factory.UpcomingEventsGroup()
    num_events = 20
    factory.Event.create_batch(size=num_events, group=group)

    patched_meetup(events=[])

    # Act
    sync_database_with_fetched_events(group)

    # Assert
    all_database_events = Event.query.all()
    assert len(all_database_events) == 0


@pytest.mark.integration
def test_sync_database(session, factory, patched_meetup):
    """
    GIVEN: table has upcoming events, fetched events contains events
            that need to be: added, updated, deleted
    WHEN: add_events_to_database is called
    THEN: table is synced with fetched event
    """
    # Arrange
    group = factory.UpcomingEventsGroup()
    event_to_update = factory.Event(group=group)
    event_to_delete = factory.Event(group=group)

    updated_event = factory.EventDetails(id=event_to_update.remote_id, venue="TBD")
    new_events = factory.EventDetails.create_batch(size=5)
    fetched_events = new_events + [updated_event]
    patched_meetup(events=fetched_events)

    # Act
    sync_database_with_fetched_events(group)

    # Assert
    assert not Event.query.get(event_to_delete.id)

    session.refresh(event_to_update)
    assert event_to_update.venue == "TBD"

    all_events_in_database = Event.query.all()
    all_event_ids_in_database = set(event.remote_id for event in all_events_in_database)
    for event in new_events:
        assert event.id in all_event_ids_in_database


@pytest.mark.unit
def test_classify_transaction_type():
    fetched_ids = [3, 4, 5, 6, 7, 10]
    database_ids = [3, 4, 5, 6, 7, 8, 9]

    result = classify_transaction_type(fetched_ids, database_ids)

    result.create == [10]
    result.delete == [8, 9]
    result.update == [3, 4, 5, 6, 7]


##########
# Test CLI
##########
@pytest.mark.end2end
def test_sync_events_database_cli(runner, session, factory, patched_meetup):
    """
    GIVEN: Empty database with a single active upcoming events configuration
    WHEN: sync_events_database is called from the CLI
    THEN: add all events to database
    """
    # Arrange
    factory.UpcomingEventsGroup(meetup_urlname="GroupName", events=[])
    events = factory.EventDetails.create_batch(size=20)
    patched_meetup(events=events)

    # Act
    runner.invoke(sync_events_database_cli)

    # Assert
    all_events_in_database = Event.query.all()
    assert len(all_events_in_database) == len(events)

    event = all_events_in_database[0]
    assert event.group.meetup_urlname == "GroupName"


@pytest.mark.end2end
def test_sync_events_database_no_active_config(
    runner, session, factory, patched_meetup
):
    """
    GIVEN: Empty database with no upcoming events configuration
    WHEN: sync_events_database is called from the CLI
    THEN: add all events to database
    """
    # Arrange
    config = factory.UpcomingEventsConfiguration(enabled=False)
    factory.UpcomingEventsGroup(
        configuration=config, meetup_urlname="GroupName", events=[]
    )
    events = factory.EventDetails.create_batch(size=20)
    patched_meetup(events=events)

    # Act
    runner.invoke(sync_events_database_cli)

    # Assert
    all_events_in_database = Event.query.all()
    assert len(all_events_in_database) == 0


@pytest.mark.end2end
def test_sync_events_database_for_multiple_active_configuration(
    runner, session, factory, patched_meetup
):
    """
    GIVEN: Empty database with multiple active events configuration
    WHEN: sync_events_database is called from the CLI
    THEN: add all events to database
    """
    # Arrange
    config = factory.UpcomingEventsConfiguration(enabled=True)
    factory.UpcomingEventsGroup(
        configuration=config, meetup_urlname="GroupName", events=[]
    )
    second_config = factory.UpcomingEventsConfiguration(enabled=True)
    factory.UpcomingEventsGroup(
        configuration=second_config, meetup_urlname="GroupName", events=[]
    )
    events = factory.EventDetails.create_batch(size=20)
    patched_meetup(events=events)

    # Act
    runner.invoke(sync_events_database_cli)

    # Assert
    all_events_in_database = Event.query.all()
    assert len(all_events_in_database) == len(events) * 2
