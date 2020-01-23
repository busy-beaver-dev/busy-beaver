import pytest

from busy_beaver.models import SyncEventDatabaseTask
from busy_beaver.apps.upcoming_events.event_database.task import (
    sync_database_with_fetched_events,
    start_sync_event_database_task,
)

MODULE_TO_TEST = "busy_beaver.apps.poller.api.update_events"


@pytest.fixture
def patched_update_events_trigger(mocker, patcher):
    return patcher(
        MODULE_TO_TEST,
        namespace=start_sync_event_database_task.__name__,
        replacement=mocker.Mock(),
    )


##################
# Integration Test
##################
@pytest.fixture
def patched_background_task(patcher, create_fake_background_task):
    return patcher(
        "busy_beaver.apps.upcoming_events.event_database.task",
        namespace=sync_database_with_fetched_events.__name__,
        replacement=create_fake_background_task(),
    )


@pytest.mark.integration
def test_poll_twitter_smoke_test(
    caplog, client, session, factory, patched_background_task
):
    # Arrange
    factory.ApiUser(username="test_user", token="abcd", role="admin")

    # Act
    client.post("/poll/sync-event-database", headers={"Authorization": "token abcd"})

    # Assert
    tasks = SyncEventDatabaseTask.query.all()
    assert len(tasks) == 1


###########
# Unit Test
###########
@pytest.mark.unit
def test_poll_events_endpoint_no_token(client, session, factory):
    # Arrange
    factory.ApiUser(username="test_user", token="abcd", role="user")

    # Act
    result = client.post("/poll/sync-event-database")

    # Assert
    assert result.status_code == 401


@pytest.mark.unit
def test_poll_events_endpoint_incorrect_token(client, session, factory):
    # Arrange
    factory.ApiUser(username="test_user", token="abcd", role="user")

    # Act
    result = client.post("/poll/sync-event-database")

    # Assert
    assert result.status_code == 401


@pytest.mark.unit
def test_poll_events_endpoint_success(
    client, session, factory, patched_update_events_trigger
):
    # Arrange
    factory.ApiUser(username="test_user", token="abcd", role="admin")

    # Act
    result = client.post(
        "/poll/sync-event-database", headers={"Authorization": "token abcd"}
    )

    # Assert
    assert result.status_code == 200
