from datetime import timedelta
import logging

import click

from .blueprint import twitter_bp
from busy_beaver.clients import twitter
from busy_beaver.common.wrappers import KeyValueStoreClient, SlackClient
from busy_beaver.config import TWITTER_USERNAME
from busy_beaver.extensions import db, rq
from busy_beaver.models import ApiUser, PostTweetTask, SlackInstallation
from busy_beaver.toolbox import set_task_progress, utc_now_minus

LAST_TWEET_KEY = "last_posted_tweet_id"
logger = logging.getLogger(__name__)
kv_store = KeyValueStoreClient()


@click.option("--channel_name", required=True, help="Slack channel")
@click.option("--workspace", required=True, help="Slack workspace ID")
@twitter_bp.cli.command("poll_twitter", help="Find new tweets to post to Slack")
def poll_twitter(channel_name: str, workspace: str):
    # TODO add logging and times
    installation = SlackInstallation.query.filter_by(workspace_id=workspace).first()
    fetch_tweets_post_to_slack(installation.id, channel_name, username=TWITTER_USERNAME)


def start_post_tweets_to_slack_task(task_owner: ApiUser, channel_name):
    # This is only used by PROD.
    # In the middle of a migration, let's not worry about if this breaks
    # Also hard coding isn't the best practice, but it's helping us get to where
    # we need to be
    logger.info("[Busy Beaver] Kick off retweeter task")

    twitter_handle = TWITTER_USERNAME
    installation = SlackInstallation.query.filter_by(workspace_id="T093FC1RC").first()
    job = fetch_tweets_post_to_slack.queue(
        installation.id, channel_name, twitter_handle
    )

    task = PostTweetTask(
        job_id=job.id,
        name="Poll Twitter",
        description="Poll Twitter for new tweets",
        user=task_owner,
        data={
            "workspace_id": "T093FC1RC",
            "channel_name": channel_name,
            "twitter_handle": twitter_handle,
        },
    )
    db.session.add(task)
    db.session.commit()


@rq.job
def fetch_tweets_post_to_slack(installation_id, channel_name, username):
    logger.info("Fetching tweets to post")
    tweets = get_tweets(installation_id, username)
    set_task_progress(33)

    tweets_to_post = _exclude_tweets_inside_window(tweets, window=timedelta(minutes=30))
    set_task_progress(67)

    logger.info("Grabbed {0} tweets".format(len(tweets_to_post)))
    # post 1 tweet at a time
    _post_to_slack(installation_id, channel_name, tweets_to_post[:1], username)
    set_task_progress(100)


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
