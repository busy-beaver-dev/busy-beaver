from datetime import timedelta
import logging

from busy_beaver import kv_store, chipy_slack
from busy_beaver.clients import twitter
from busy_beaver.config import TWITTER_USERNAME
from busy_beaver.extensions import db, rq
from busy_beaver.models import ApiUser, PostTweetTask
from busy_beaver.toolbox import utc_now_minus, set_task_progress

LAST_TWEET_KEY = "last_posted_tweet_id"
logger = logging.getLogger(__name__)


def start_post_tweets_to_slack_task(task_owner: ApiUser, channel_name):
    logger.info("[Busy Beaver] Kick off retweeter task")

    twitter_handle = TWITTER_USERNAME
    job = fetch_tweets_post_to_slack.queue(channel_name, twitter_handle)

    task = PostTweetTask(
        job_id=job.id,
        name="Poll Twitter",
        description="Poll Twitter for new tweets",
        user=task_owner,
        data={"channel_name": channel_name, "twitter_handle": twitter_handle},
    )
    db.session.add(task)
    db.session.commit()


@rq.job
def fetch_tweets_post_to_slack(channel_name, username):
    logger.info("[Busy Beaver] Fetching tweets to post")
    tweets = get_tweets(username)
    set_task_progress(33)

    tweets_to_post = _exclude_tweets_inside_window(tweets, window=timedelta(minutes=30))
    set_task_progress(67)

    logger.info("[Busy Beaver] Grabbed {0} tweets".format(len(tweets_to_post)))
    _post_to_slack(channel_name, tweets_to_post[:1], username)  # post 1 tweet at a time
    set_task_progress(100)


def get_tweets(username):
    """Get latest tweets after last_posted_tweet_id"""
    tweets = twitter.get_user_timeline(username)
    last_posted_tweet_id = kv_store.get_int(LAST_TWEET_KEY)
    recent_tweets = [tweet for tweet in tweets if tweet.id > last_posted_tweet_id]
    return list(reversed(recent_tweets))


def _exclude_tweets_inside_window(tweets, *, window: timedelta):
    """Buffer to delete tweets before retweeting to Slack"""
    boundary_dt = utc_now_minus(window)
    return [tweet for tweet in tweets if tweet.created_at <= boundary_dt]


def _post_to_slack(channel_name, tweets, twitter_username):
    """Twitter Slack app unfurls URLs in Slack to show tweet details"""
    url = "https://twitter.com/{username}/statuses/{id}"
    for tweet in tweets:
        tweet_url = url.format(username=twitter_username, id=tweet.id)
        chipy_slack.post_message(tweet_url, channel=channel_name)
        kv_store.put_int(LAST_TWEET_KEY, tweet.id)
