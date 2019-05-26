import pytest

from busy_beaver.models import AddNewEventsToDatabaseTask
from busy_beaver.apps.events_database.task import (
    add_new_events_to_database,
    start_add_new_events_to_database_task,
)

MODULE_TO_TEST = "busy_beaver.blueprints.poller.update_events"


@pytest.fixture
def patched_update_events_trigger(mocker, patcher):
    return patcher(
        MODULE_TO_TEST,
        namespace=start_add_new_events_to_database_task.__name__,
        replacement=mocker.Mock(),
    )


##################
# Integration Test
##################
@pytest.fixture
def patched_background_task(patcher, create_fake_background_task):
    return patcher(
        "busy_beaver.apps.events_database.task",
        namespace=add_new_events_to_database.__name__,
        replacement=create_fake_background_task(),
    )


@pytest.mark.integration
def test_poll_twitter_smoke_test(
    caplog, client, session, create_api_user, patched_background_task
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="admin")

    # Act
    client.post("/poll/events", headers={"Authorization": "token abcd"})

    # Assert
    tasks = AddNewEventsToDatabaseTask.query.all()
    assert len(tasks) == 1


###########
# Unit Test
###########
@pytest.mark.unit
def test_poll_events_endpoint_no_token(client, session, create_api_user):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="user")

    # Act
    result = client.post("/poll/events")

    # Assert
    assert result.status_code == 401


@pytest.mark.unit
def test_poll_events_endpoint_incorrect_token(client, session, create_api_user):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="user")

    # Act
    result = client.post("/poll/events")

    # Assert
    assert result.status_code == 401


@pytest.mark.unit
def test_poll_events_endpoint_success(
    client, session, create_api_user, patched_update_events_trigger
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="admin")

    # Act
    result = client.post("/poll/events", headers={"Authorization": "token abcd"})

    # Assert
    assert result.status_code == 200
