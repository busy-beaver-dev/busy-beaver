import pytest

from busy_beaver.models import ApiUser
from busy_beaver.apps.events_database.task import (
    add_new_events_to_database,
    start_add_new_events_to_database_task,
)
from busy_beaver.factories.event import EventFactory
from busy_beaver.factories.event_details import EventDetailsFactory
from busy_beaver.models import Event

MODULE_TO_TEST = "busy_beaver.apps.events_database.task"


#######################
# Test Trigger Function
#######################
@pytest.fixture
def patched_background_task(patcher, create_fake_background_task):
    return patcher(
        MODULE_TO_TEST,
        namespace=add_new_events_to_database.__name__,
        replacement=create_fake_background_task(),
    )


@pytest.mark.unit
def test_start_add_new_events_task(session, create_api_user, patched_background_task):
    """Test trigger function"""
    # Arrange
    api_user = create_api_user("admin")

    # Act
    start_add_new_events_to_database_task(api_user)

    # Assert
    api_user = ApiUser.query.get(api_user.id)
    task = api_user.tasks[0]
    assert task.job_id == patched_background_task.id


#####################
# Test Background Job
#####################
@pytest.fixture
def patched_meetup(patcher):
    class FakeMeetupAdapter:
        def __init__(self, events):
            self.events = events

        def get_events(self, group_name, count):
            return self.events

    def _wrapper(events):
        fake_meetup = FakeMeetupAdapter(events)
        patcher(MODULE_TO_TEST, namespace="meetup", replacement=fake_meetup)

    return _wrapper


@pytest.mark.integration
def test_add_all_events_to_database(session, patched_meetup):
    """
    GIVEN: Empty database
    WHEN: add_new_events_to_database is called
    THEN: add all events to database
    """
    # Arrange
    events = EventDetailsFactory.create_batch(size=20)
    patched_meetup(events=events)

    # Act
    add_new_events_to_database("test_group")

    # Assert
    all_events_in_database = Event.query.all()
    assert len(all_events_in_database) == len(events)


@pytest.mark.integration
def test_add_new_events_to_database(session, patched_meetup):
    """
    GIVEN: table containing event
    WHEN: add_new_events_to_database is called
    THEN: add additional event that is not already in database to database
    """
    # Arrange
    event_in_db = EventFactory()

    num_new_events = 5
    events = EventDetailsFactory.create_batch(size=num_new_events)
    events.append(EventDetailsFactory(id=event_in_db.remote_id))
    patched_meetup(events=events)

    # Act
    add_new_events_to_database("test_group")

    # Assert
    all_events_in_database = Event.query.all()
    assert len(all_events_in_database) == num_new_events + 1
