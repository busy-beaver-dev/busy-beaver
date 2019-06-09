import pytest

from busy_beaver.models import ApiUser
from busy_beaver.apps.events_database.task import (
    sync_database_with_fetched_events,
    start_sync_events_database_task,
)
from busy_beaver.factories.event import EventFactory
from busy_beaver.factories.event_details import EventDetailsFactory
from busy_beaver.models import Event
from tests.utilities import FakeMeetupAdapter

MODULE_TO_TEST = "busy_beaver.apps.events_database.task"


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
def test_start_add_events_task(session, create_api_user, patched_background_task):
    """Test trigger function"""
    # Arrange
    api_user = create_api_user("admin")

    # Act
    start_sync_events_database_task(api_user)

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
def test_add_all_events_to_database(session, patched_meetup):
    """
    GIVEN: Empty database
    WHEN: add_events_to_database is called
    THEN: add all events to database
    """
    # Arrange
    events = EventDetailsFactory.create_batch(size=20)
    patched_meetup(events=events)

    # Act
    sync_database_with_fetched_events("test_group")

    # Assert
    all_events_in_database = Event.query.all()
    assert len(all_events_in_database) == len(events)


@pytest.mark.integration
def test_update_all_events_in_database(session, patched_meetup):
    """
    GIVEN: table contains upcoming events, adapter has same events with updated details
    WHEN: add_events_to_database is called
    THEN: update event information in database
    """
    # Arrange
    num_events = 20
    database_events = EventFactory.create_batch(size=num_events)
    [session.add(event) for event in database_events]
    session.commit()

    fetched_events = []
    for event in database_events:
        fetched_events.append(EventDetailsFactory(id=event.remote_id, venue="TBD"))
    patched_meetup(events=fetched_events)

    # Act
    sync_database_with_fetched_events("test_group")

    # Assert
    all_database_events = Event.query.all()
    assert len(all_database_events) == num_events
    for event in all_database_events:
        assert event.venue == "TBD"


@pytest.mark.integration
def test_delete_all_events_in_database(session, patched_meetup):
    """
    GIVEN: table contains upcoming events, adapter has no events
    WHEN: add_events_to_database is called
    THEN: all events are removed fromd atabase
    """
    # Arrange
    num_events = 20
    database_events = EventFactory.create_batch(size=num_events)
    [session.add(event) for event in database_events]
    session.commit()

    patched_meetup(events=[])

    # Act
    sync_database_with_fetched_events("test_group")

    # Assert
    all_database_events = Event.query.all()
    assert len(all_database_events) == 0


@pytest.mark.integration
@pytest.mark.current
def test_sync_database(session, patched_meetup):
    """
    GIVEN: table has upcoming events, fetched events contains events
            that need to be: added, updated, deleted
    WHEN: add_events_to_database is called
    THEN: table is synced with fetched event
    """
    # Arrange
    event_to_update = EventFactory()
    session.add(event_to_update)
    event_to_delete = EventFactory()
    session.add(event_to_delete)
    session.commit()

    updated_event = EventDetailsFactory(id=event_to_update.remote_id, venue="TBD")
    new_events = EventDetailsFactory.create_batch(size=5)
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
