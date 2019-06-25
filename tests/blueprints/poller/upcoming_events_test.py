import pytest
from busy_beaver.blueprints.poller.upcoming_events import (
    post_upcoming_events_message_to_slack,
)

MODULE_TO_TEST = "busy_beaver.blueprints.poller.upcoming_events"


@pytest.fixture
def patched_post_upcoming_events_function(mocker, patcher):
    return patcher(
        MODULE_TO_TEST,
        namespace=post_upcoming_events_message_to_slack.__name__,
        replacement=mocker.Mock(),
    )


@pytest.mark.unit
def test_post_upcoming_events_endpoint_no_token(
    client, session, fm, patched_post_upcoming_events_function
):
    # Arrange
    fm.ApiUserFactory(username="test_user", token="abcd", role="user")

    # Act
    result = client.post("/poll/upcoming-events")

    # Assert
    assert result.status_code == 401


@pytest.mark.unit
def test_post_upcoming_events_endpoint_incorrect_token(
    client, session, fm, patched_post_upcoming_events_function
):
    # Arrange
    fm.ApiUserFactory(username="test_user", token="abcd", role="user")

    # Act
    result = client.post("/poll/upcoming-events")

    # Assert
    assert result.status_code == 401


@pytest.mark.unit
def test_post_upcoming_events_endpoint_empty_body(
    caplog, client, session, fm, patched_post_upcoming_events_function
):
    # Arrange
    fm.ApiUserFactory(username="test_user", token="abcd", role="admin")

    # Act
    result = client.post(
        "/poll/upcoming-events", headers={"Authorization": "token abcd"}
    )

    # Assert
    assert result.status_code == 422


@pytest.mark.unit
def test_post_upcoming_events_endpoint_success(
    caplog, client, session, fm, patched_post_upcoming_events_function
):
    # Arrange
    fm.ApiUserFactory(username="test_user", token="abcd", role="admin")
    mock = patched_post_upcoming_events_function

    # Act
    result = client.post(
        "/poll/upcoming-events",
        headers={"Authorization": "token abcd"},
        json={"channel": "announcements"},
    )

    # Assert
    assert result.status_code == 200
    args, kwargs = mock.call_args
    assert "announcements" in kwargs["channel"]
