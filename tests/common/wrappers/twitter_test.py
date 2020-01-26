import os

import pytest

from busy_beaver.common.wrappers.twitter import TwitterClient


@pytest.fixture
def client():
    TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY", "test")
    TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET", "test")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "test")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "test")
    yield TwitterClient(
        TWITTER_CONSUMER_KEY,
        TWITTER_CONSUMER_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET,
    )


@pytest.mark.vcr()
def test_get_user_timeline(client):
    tweets = client.get_user_timeline()

    assert len(tweets) == 20


@pytest.mark.vcr()
def test_get_last_tweet_id(client):
    last_id = client.get_last_tweet_id()

    assert isinstance(last_id, int)
