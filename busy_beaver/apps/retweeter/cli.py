import logging

import click

from .blueprint import twitter_bp
from .task import fetch_tweets_post_to_slack
from busy_beaver.config import TWITTER_USERNAME
from busy_beaver.models import SlackInstallation

logger = logging.getLogger(__name__)


@click.option("--channel_name", required=True, help="Slack channel")
@click.option("--workspace", required=True, help="Slack workspace ID")
@twitter_bp.cli.command("poll_twitter", help="Find new tweets to post to Slack")
def poll_twitter(channel_name: str, workspace: str):
    # TODO add logging and times
    installation = SlackInstallation.query.filter_by(workspace_id=workspace).first()
    fetch_tweets_post_to_slack(installation.id, channel_name, username=TWITTER_USERNAME)
