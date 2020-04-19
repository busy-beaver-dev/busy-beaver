from datetime import timedelta
import logging

from busy_beaver.clients import twitter
from busy_beaver.common.wrappers import KeyValueStoreClient, SlackClient
from busy_beaver.models import SlackInstallation
from busy_beaver.toolbox import utc_now_minus

LAST_TWEET_KEY = "last_posted_tweet_id"
logger = logging.getLogger(__name__)
kv_store = KeyValueStoreClient()


def fetch_tweets_post_to_slack(installation_id, channel_name, username):
    logger.info("Fetching tweets to post")
    tweets = get_tweets(installation_id, username)

    tweets_to_post = _exclude_tweets_inside_window(tweets, window=timedelta(minutes=30))

    logger.info("Grabbed {0} tweets".format(len(tweets_to_post)))
    # post 1 tweet at a time
    _post_to_slack(installation_id, channel_name, tweets_to_post[:1], username)


def get_tweets(installation_id, username):
    """Get latest tweets after last_posted_tweet_id"""
    tweets = twitter.get_user_timeline(username)
    last_posted_tweet_id = kv_store.get_int(installation_id, LAST_TWEET_KEY)
    recent_tweets = [tweet for tweet in tweets if tweet.id > last_posted_tweet_id]
    return list(reversed(recent_tweets))


def _exclude_tweets_inside_window(tweets, *, window: timedelta):
    """Buffer to delete tweets before retweeting to Slack"""
    boundary_dt = utc_now_minus(window)
    return [tweet for tweet in tweets if tweet.created_at <= boundary_dt]


def _post_to_slack(installation_id, channel_name, tweets, twitter_username):
    """Twitter Slack app unfurls URLs in Slack to show tweet details"""
    slack_installation = SlackInstallation.query.get(installation_id)
    slack = SlackClient(slack_installation.bot_access_token)

    url = "https://twitter.com/{username}/statuses/{id}"
    for tweet in tweets:
        tweet_url = url.format(username=twitter_username, id=tweet.id)
        slack.post_message(tweet_url, channel=channel_name)
        kv_store.put_int(installation_id, LAST_TWEET_KEY, tweet.id)
