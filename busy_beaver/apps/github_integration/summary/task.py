import logging
import random
from typing import List

from sqlalchemy import and_

from .blocks import GitHubSummaryPost
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.models import GitHubSummaryUser

logger = logging.getLogger(__name__)


def fetch_github_summary_post_to_slack(installation, boundary_dt):
    channel = installation.github_summary_config.channel
    slack = SlackClient(installation.bot_access_token)

    channel_members = slack.get_channel_members(channel)
    users: List[GitHubSummaryUser] = GitHubSummaryUser.query.filter(
        and_(
            GitHubSummaryUser.config_id == installation.github_summary_config.id,
            GitHubSummaryUser.slack_id.in_(channel_members),
            GitHubSummaryUser.github_username.isnot(None),
        )
    ).all()
    random.shuffle(users)

    github_summary_post = GitHubSummaryPost(users, boundary_dt)
    github_summary_post.create()

    slack.post_message(
        blocks=github_summary_post.as_blocks(),
        channel=channel,
        unfurl_links=False,
        unfurl_media=False,
    )
