from datetime import timedelta
import logging
import random
from typing import List

from sqlalchemy import and_

from .blocks import GitHubSummaryPost
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.exceptions import ValidationError
from busy_beaver.extensions import rq
from busy_beaver.models import GitHubSummaryUser, SlackInstallation
from busy_beaver.toolbox import set_task_progress, utc_now_minus

logger = logging.getLogger(__name__)


@rq.job
def post_github_summary_message(workspace_id: str):
    installation = SlackInstallation.query.filter_by(workspace_id=workspace_id).first()
    if not installation:
        raise ValidationError("workspace not found")

    boundary_dt = utc_now_minus(timedelta(days=1))
    fetch_github_summary_post_to_slack(installation, boundary_dt)
    set_task_progress(100)


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

    # TODO: make async
    # take list of users, boundary date
    # get a list of all their activity

    # pass in users + activity into github summary post to format

    github_summary_post = GitHubSummaryPost(users, boundary_dt)
    slack.post_message(
        blocks=github_summary_post.as_blocks(),
        channel=channel,
        unfurl_links=False,
        unfurl_media=False,
    )
