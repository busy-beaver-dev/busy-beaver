# required feature: env variable - min time to wait before posting tweet
# create endpoint that kicks off this process
# run with cron, add task to ansible script
# how to disable bot from posting, keyword in tweet?

from datetime import timedelta
import logging

import tweepy
from . import slack
from .config import (
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
)
from .models import kv_store
from .toolbox import utc_now_minus

logger = logging.getLogger(__name__)

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

LAST_TWEET_KEY = "last_posted_tweet_id"


def get_tweets(twitter_username):
    """Get latest tweets after last_posted_tweet_id"""
    tweets = api.user_timeline(screen_name=twitter_username, tweet_mode="extended")
    last_posted_tweet_id = kv_store.get_int(LAST_TWEET_KEY)
    recent_tweets = [tweet for tweet in tweets if tweet.id > last_posted_tweet_id]
    return list(reversed(recent_tweets))


def exclude_recent_tweets(tweets):
    """Buffer to delete tweets before retweeting to Slack"""
    # TODO make timedelta a parameter
    boundary_dt = utc_now_minus(timedelta(minutes=30)).replace(tzinfo=None)
    return [tweet for tweet in tweets if tweet.created_at <= boundary_dt]


def post_to_slack(username, tweets, channel="bot-testing"):
    message = "https://twitter.com/{username}/statuses/{id}"
    channel_id = slack.get_channel_id(channel)
    for tweet in tweets:
        slack.post_message(channel_id, message.format(username=username, id=tweet.id))
        kv_store.put_int(LAST_TWEET_KEY, tweet.id)


def main(username="ChicagoPython"):
    logger.info("Posting tweets")
    tweets = get_tweets(username)
    tweets_to_post = exclude_recent_tweets(tweets)
    logger.info("{0}".format(len(tweets_to_post)))
    post_to_slack(username, tweets_to_post)


if __name__ == "__main__":
    main()
