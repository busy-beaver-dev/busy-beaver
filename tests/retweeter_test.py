from datetime import timedelta
import pytest

from busy_beaver.adapters.twitter import Tweet
from busy_beaver.retweeter import post_tweets_to_slack, LAST_TWEET_KEY
from busy_beaver.toolbox import utc_now_minus

MODULE_TO_TEST = "busy_beaver.retweeter"


@pytest.fixture
def patcher(monkeypatch):
    """Helper to patch in the correct spot"""

    def _patcher(namespace, replacement_object):
        namespace_to_patch = f"{MODULE_TO_TEST}.{namespace}"
        monkeypatch.setattr(namespace_to_patch, replacement_object)
        return replacement_object

    yield _patcher


@pytest.fixture
def patched_twitter(patcher):
    class FakeTwitter:
        def __init__(self, tweets):
            self.tweets = tweets

        def get_user_timeline(self, username):
            return self.tweets

    def _wrapper(tweets):
        fake_twitter = FakeTwitter(tweets)
        patcher("twitter", fake_twitter)

    return _wrapper


@pytest.fixture
def patched_slack(patcher):
    def _wrapper(mock_to_return):
        return patcher("slack", mock_to_return)

    return _wrapper


@pytest.mark.integration
def test_post_tweets_to_slack(mocker, kv_store, patched_twitter, patched_slack):
    """
    GIVEN: 3 tweets to post (2 within the window)
    WHEN: post_tweets_to_slack is called
    THEN: we post one tweet
    """
    # Arrange
    kv_store.put_int(LAST_TWEET_KEY, 0)
    tweets = [
        Tweet(3, utc_now_minus(timedelta())),
        Tweet(2, utc_now_minus(timedelta(days=1))),
        Tweet(1, utc_now_minus(timedelta(days=1))),
    ]
    patched_twitter(tweets)
    slack = patched_slack(mocker.MagicMock())

    # Act
    post_tweets_to_slack("test_username", "test_channel")

    # Assert
    assert len(slack.mock_calls) == 1
    args, kwargs = slack.post_message.call_args
    assert "test_username/statuses/1" in args[0]
    assert "test_channel" in kwargs["channel"]
