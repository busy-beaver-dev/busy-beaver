from datetime import timedelta
import logging
import random
from typing import List

import click
from sqlalchemy import and_

from ..blueprint import github_bp
from .blocks import GitHubSummaryPost
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.exceptions import ValidationError
from busy_beaver.models import GitHubSummaryUser, SlackInstallation
from busy_beaver.toolbox import utc_now_minus

logger = logging.getLogger(__name__)


@click.option("--workspace", required=True)  # Slack Workspace ID
@github_bp.cli.command("post_github_summary", help="Post a GitHub summary")
def post_github_summary_to_slack_cli(workspace: str):
    boundary_dt = utc_now_minus(timedelta(days=1))
    slack_installation = SlackInstallation.query.filter_by(
        workspace_id=workspace
    ).first()
    if not slack_installation:
        raise ValidationError("workspace not found")

    # we should log that we did something somewhere
    # also keep track of how long a summary took
    # TODO once we are migrated over
    fetch_github_summary_post_to_slack(slack_installation.id, boundary_dt)


def fetch_github_summary_post_to_slack(installation_id, boundary_dt):
    slack_installation = SlackInstallation.query.get(installation_id)
    channel = slack_installation.github_summary_config.channel
    slack = SlackClient(slack_installation.bot_access_token)

    channel_members = slack.get_channel_members(channel)
    users: List[GitHubSummaryUser] = GitHubSummaryUser.query.filter(
        and_(
            GitHubSummaryUser.installation_id == installation_id,
            GitHubSummaryUser.slack_id.in_(channel_members),
            GitHubSummaryUser.github_username.isnot(None),
        )
    ).all()
    random.shuffle(users)

    github_summary_post = GitHubSummaryPost(users, boundary_dt)
    github_summary_post.create()

    # message = ""
    # for idx, user in enumerate(users):
    #     logger.info("Compiling stats for {0}".format(user))
    #     user_events = GitHubUserEvents(user, boundary_dt)
    #     message += user_events.generate_summary_text()

    # if not message:
    #     message = (
    #         '"If code falls outside version control, and no one is around to read it, '
    #         'does it make a sound?" - Zax Rosenberg'
    #     )

    slack.post_message(
        blocks=github_summary_post.as_blocks(),
        channel=channel,
        unfurl_links=False,
        unfurl_media=False,
    )
