# required feature: env variable - min time to wait before posting tweet
# create endpoint that kicks off this process
# run with cron, add task to ansible script
# how to disable bot from posting, keyword in tweet?

from datetime import timedelta
import logging

from . import slack, twitter
from .models import kv_store
from .toolbox import utc_now_minus

logger = logging.getLogger(__name__)


LAST_TWEET_KEY = "last_posted_tweet_id"


def get_tweets(username):
    """Get latest tweets after last_posted_tweet_id"""
    tweets = twitter.get_user_timeline(username)
    last_posted_tweet_id = kv_store.get_int(LAST_TWEET_KEY)
    recent_tweets = [tweet for tweet in tweets if tweet.id_ > last_posted_tweet_id]
    return list(reversed(recent_tweets))


def exclude_recent_tweets(tweets):
    """Buffer to delete tweets before retweeting to Slack"""
    # TODO make timedelta a parameter
    boundary_dt = utc_now_minus(timedelta(minutes=30))
    return [tweet for tweet in tweets if tweet.created_at <= boundary_dt]


def post_to_slack(username, tweets, channel):
    message = "https://twitter.com/{username}/statuses/{id}"
    channel_id = slack.get_channel_id(channel)
    for tweet in tweets:
        slack.post_message(channel_id, message.format(username=username, id=tweet.id_))
        kv_store.put_int(LAST_TWEET_KEY, tweet.id_)


def main(username, channel):
    logger.info("Posting tweets")
    tweets = get_tweets(username)
    tweets_to_post = exclude_recent_tweets(tweets)
    logger.info("{0}".format(len(tweets_to_post)))
    post_to_slack(username, tweets_to_post, channel)
