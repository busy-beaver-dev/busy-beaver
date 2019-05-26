import pytest

from busy_beaver.blueprints.poller.retweeter import start_post_tweets_to_slack_task
from busy_beaver.models import PostTweetTask
from busy_beaver.tasks.retweeter import fetch_tweets_post_to_slack

MODULE_TO_TEST = "busy_beaver.blueprints.poller.retweeter"


@pytest.fixture
def patched_retweeter_trigger(mocker, patcher):
    return patcher(
        MODULE_TO_TEST,
        namespace=start_post_tweets_to_slack_task.__name__,
        replacement=mocker.Mock(),
    )


##################
# Integration Test
##################
@pytest.fixture
def patched_background_task(patcher, create_fake_background_task):
    return patcher(
        "busy_beaver.tasks.retweeter",
        namespace=fetch_tweets_post_to_slack.__name__,
        replacement=create_fake_background_task(),
    )


@pytest.mark.integration
def test_poll_twitter_smoke_test(
    caplog, client, session, create_api_user, patched_background_task
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="admin")

    #  Act
    client.post(
        "/poll-twitter",
        headers={"Authorization": "token abcd"},
        json={"channel": "general"},
    )

    # Assert
    tasks = PostTweetTask.query.all()
    assert len(tasks) == 1


###########
# Unit Test
###########
@pytest.mark.unit
def test_poll_twitter_endpoint_no_token(
    client, session, create_api_user, patched_retweeter_trigger
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="user")

    #  Act
    result = client.post("/poll-twitter")

    # Assert
    assert result.status_code == 401


@pytest.mark.unit
def test_poll_twitter_endpoint_incorrect_token(
    client, session, create_api_user, patched_retweeter_trigger
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="user")

    #  Act
    result = client.post("/poll-twitter")

    # Assert
    assert result.status_code == 401


@pytest.mark.unit
def test_poll_twitter_endpoint_empty_body(
    caplog, client, session, create_api_user, patched_retweeter_trigger
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="admin")

    #  Act
    result = client.post("/poll-twitter", headers={"Authorization": "token abcd"})

    # Assert
    assert result.status_code == 422


@pytest.mark.unit
def test_poll_twitter_endpoint_success(
    caplog, client, session, create_api_user, patched_retweeter_trigger
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="admin")
    mock = patched_retweeter_trigger

    #  Act
    result = client.post(
        "/poll-twitter",
        headers={"Authorization": "token abcd"},
        json={"channel": "general"},
    )

    # Assert
    assert result.status_code == 200
    args, kwargs = mock.call_args
    assert kwargs["channel_name"] == "general"
