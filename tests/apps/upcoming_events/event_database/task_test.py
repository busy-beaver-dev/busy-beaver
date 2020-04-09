import pytest
from tests._utilities import FakeMeetupAdapter

from busy_beaver.apps.upcoming_events.event_database.task import (
    start_sync_event_database_task,
    sync_database_with_fetched_events,
    sync_events_database_cli,
)
from busy_beaver.models import ApiUser, Event

MODULE_TO_TEST = "busy_beaver.apps.upcoming_events.event_database.task"


#######################
# Test Trigger Function
#######################
@pytest.fixture
def patched_background_task(patcher, create_fake_background_task):
    return patcher(
        MODULE_TO_TEST,
        namespace=sync_database_with_fetched_events.__name__,
        replacement=create_fake_background_task(),
    )


@pytest.mark.unit
def test_start_add_events_task(session, factory, patched_background_task):
    """Test trigger function"""
    # Arrange
    api_user = factory.ApiUser(username="admin")

    # Act
    start_sync_event_database_task(api_user)

    # Assert
    api_user = ApiUser.query.get(api_user.id)
    task = api_user.tasks[0]
    assert task.job_id == patched_background_task.id


#####################
# Test Background Job
#####################
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
    events = factory.EventDetails.create_batch(size=20)
    patched_meetup(events=events)

    # Act
    sync_database_with_fetched_events("test_group")

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
    num_events = 20
    database_events = factory.Event.create_batch(size=num_events)

    fetched_events = []
    for event in database_events:
        fetched_events.append(factory.EventDetails(id=event.remote_id, venue="TBD"))
    patched_meetup(events=fetched_events)

    # Act
    sync_database_with_fetched_events("test_group")

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
    num_events = 20
    factory.Event.create_batch(size=num_events)

    patched_meetup(events=[])

    # Act
    sync_database_with_fetched_events("test_group")

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
    event_to_update = factory.Event()
    event_to_delete = factory.Event()

    updated_event = factory.EventDetails(id=event_to_update.remote_id, venue="TBD")
    new_events = factory.EventDetails.create_batch(size=5)
    fetched_events = new_events + [updated_event]
    patched_meetup(events=fetched_events)

    # Act
    sync_database_with_fetched_events("test_group")

    # Assert
    assert not Event.query.get(event_to_delete.id)

    session.refresh(event_to_update)
    assert event_to_update.venue == "TBD"

    all_events_in_database = Event.query.all()
    all_event_ids_in_database = set(event.remote_id for event in all_events_in_database)
    for event in new_events:
        assert event.id in all_event_ids_in_database


##########
# Test CLI
##########
@pytest.mark.end2end
def test_sync_events_database_cli(runner, session, factory, patched_meetup):
    """
    GIVEN: Empty database
    WHEN: add_events_to_database is called
    THEN: add all events to database
    """
    # Arrange
    events = factory.EventDetails.create_batch(size=20)
    patched_meetup(events=events)

    # Act
    runner.invoke(sync_events_database_cli, ["--group_name", "test_group"])

    # Assert
    all_events_in_database = Event.query.all()
    assert len(all_events_in_database) == len(events)
