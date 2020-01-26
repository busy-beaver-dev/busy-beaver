from datetime import timedelta
import logging
import random
from typing import List

from sqlalchemy import and_

from .summary import GitHubUserEvents
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.exceptions import ValidationError
from busy_beaver.extensions import db, rq
from busy_beaver.models import (
    ApiUser,
    GitHubSummaryUser,
    PostGitHubSummaryTask,
    SlackInstallation,
)
from busy_beaver.toolbox import set_task_progress, utc_now_minus

logger = logging.getLogger(__name__)


def start_post_github_summary_task(task_owner: ApiUser, workspace_id: str):
    boundary_dt = utc_now_minus(timedelta(days=1))
    slack_installation = SlackInstallation.query.filter_by(
        workspace_id=workspace_id
    ).first()
    if not slack_installation:
        raise ValidationError("workspace not found")

    job = fetch_github_summary_post_to_slack.queue(slack_installation.id, boundary_dt)

    task = PostGitHubSummaryTask(
        job_id=job.id,
        name="Post GitHub Summary",
        description="Daily task to post GitHub Summary",
        user=task_owner,
        data={
            "workspace_id": workspace_id,
            "slack_installation_id": slack_installation.id,
            "boundary_dt": boundary_dt.isoformat(),
        },
    )
    db.session.add(task)
    db.session.commit()


@rq.job
def fetch_github_summary_post_to_slack(installation_id, boundary_dt):
    slack_installation = SlackInstallation.query.get(installation_id)
    channel = slack_installation.github_summary_config.channel
    slack = SlackClient(slack_installation.bot_access_token)

    channel_info = slack.get_channel_info(channel)
    users: List[GitHubSummaryUser] = GitHubSummaryUser.query.filter(
        and_(
            GitHubSummaryUser.installation_id == installation_id,
            GitHubSummaryUser.slack_id.in_(channel_info.members),
            GitHubSummaryUser.github_username.isnot(None),
        )
    ).all()
    random.shuffle(users)

    message = ""
    num_users = len(users)
    for idx, user in enumerate(users):
        logger.info("[Busy Beaver] Compiling stats for {0}".format(user))
        user_events = GitHubUserEvents(user, boundary_dt)
        message += user_events.generate_summary_text()
        set_task_progress(idx / (num_users + 1) * 100)

    if not message:
        message = (
            '"If code falls outside version control, and no one is around to read it, '
            'does it make a sound?" - Zax Rosenberg'
        )

    slack.post_message(
        message=message, channel=channel, unfurl_links=False, unfurl_media=False
    )
    set_task_progress(100)
