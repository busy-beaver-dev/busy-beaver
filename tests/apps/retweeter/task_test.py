from datetime import timedelta
import pytest

from busy_beaver.apps.retweeter.task import (
    fetch_tweets_post_to_slack,
    LAST_TWEET_KEY,
    start_post_tweets_to_slack_task,
)
from busy_beaver.models import ApiUser
from busy_beaver.toolbox import utc_now_minus
from tests._utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.apps.retweeter.task"


#######################
# Test Trigger Function
#######################
@pytest.fixture
def patched_background_task(patcher, create_fake_background_task):
    return patcher(
        MODULE_TO_TEST,
        namespace=fetch_tweets_post_to_slack.__name__,
        replacement=create_fake_background_task(),
    )


@pytest.mark.unit
def test_start_post_tweet_task(session, fm, patched_background_task):
    """Test trigger function"""
    # Arrange
    api_user = fm.ApiUserFactory(username="admin")
    channel_name = "test-channel"

    # Act
    start_post_tweets_to_slack_task(api_user, channel_name)

    # Assert
    api_user = ApiUser.query.get(api_user.id)
    task = api_user.tasks[0]
    assert task.job_id == patched_background_task.id
    assert task.data["channel_name"] == channel_name


#####################
# Test Background Job
#####################
@pytest.fixture
def patched_twitter(patcher):
    class FakeTwitter:
        def __init__(self, tweets):
            self.tweets = tweets

        def get_user_timeline(self, username):
            return self.tweets

    def _wrapper(tweets):
        fake_twitter = FakeTwitter(tweets)
        patcher(MODULE_TO_TEST, namespace="twitter", replacement=fake_twitter)

    return _wrapper


@pytest.fixture
def patched_slack(patcher):
    obj = FakeSlackClient()
    return patcher(MODULE_TO_TEST, namespace="chipy_slack", replacement=obj)


# Technically it's an integration test (tests more than one function)
# but it's a unit test that should be around a class
# TODO make the retweeter module into a class
@pytest.mark.integration
def test_post_tweets_to_slack(mocker, fm, kv_store, patched_twitter, patched_slack):
    """
    GIVEN: 3 tweets to post (2 within the window)
    WHEN: post_tweets_to_slack is called
    THEN: we post one tweet
    """
    # Arrange
    kv_store.put_int(LAST_TWEET_KEY, 0)
    tweets = [
        fm.TweetFactory(id=3, created_at=utc_now_minus(timedelta())),
        fm.TweetFactory(id=2, created_at=utc_now_minus(timedelta(days=1))),
        fm.TweetFactory(id=1, created_at=utc_now_minus(timedelta(days=1))),
    ]
    patched_twitter(tweets)

    # Act
    fetch_tweets_post_to_slack("test_channel", "test_username")

    # Assert
    assert len(patched_slack.mock.mock_calls) == 1
    args, kwargs = patched_slack.mock.call_args
    assert "test_username/statuses/1" in args[0]
    assert "test_channel" in kwargs["channel"]
