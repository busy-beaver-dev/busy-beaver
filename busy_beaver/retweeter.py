from datetime import timedelta
import logging

from . import slack, twitter
from .models import kv_store
from .toolbox import utc_now_minus

LAST_TWEET_KEY = "last_posted_tweet_id"
logger = logging.getLogger(__name__)


def post_tweets_to_slack(username, channel, ):
    logger.info("[Busy-Beaver] Fetching tweets to post")
    tweets = get_tweets(username)
    tweets_to_post = exclude_tweets_inside_window(tweets, window=timedelta(minutes=30))
    logger.info("[Busy-Beaver] Grabbed {0} tweets".format(len(tweets_to_post)))
    post_to_slack(channel, tweets_to_post[:1], username)  # post 1 tweet at a time


def get_tweets(username):
    """Get latest tweets after last_posted_tweet_id"""
    tweets = twitter.get_user_timeline(username)
    last_posted_tweet_id = kv_store.get_int(LAST_TWEET_KEY)
    recent_tweets = [tweet for tweet in tweets if tweet.id > last_posted_tweet_id]
    return list(reversed(recent_tweets))


def exclude_tweets_inside_window(tweets, *, window: timedelta):
    """Buffer to delete tweets before retweeting to Slack"""
    boundary_dt = utc_now_minus(window)
    return [tweet for tweet in tweets if tweet.created_at <= boundary_dt]


def post_to_slack(channel, tweets, twitter_username):
    """Twitter Slack app unfurls URLs in Slack to show tweet details"""
    url = "https://twitter.com/{username}/statuses/{id}"
    for tweet in tweets:
        tweet_url = url.format(username=twitter_username, id=tweet.id)
        slack.post_message(tweet_url, channel=channel)
        kv_store.put_int(LAST_TWEET_KEY, tweet.id)
