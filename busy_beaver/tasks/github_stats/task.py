from datetime import timedelta
import logging
import random
from typing import List

from sqlalchemy import and_

from ..toolbox import set_task_progress
from .summary import GitHubUserEvents
from busy_beaver import slack
from busy_beaver.extensions import db, rq
from busy_beaver.models import ApiUser, User, PostGitHubSummaryTask
from busy_beaver.toolbox import utc_now_minus

logger = logging.getLogger(__name__)


def start_post_github_summary_task(task_owner: ApiUser, channel_name: str):
    boundary_dt = utc_now_minus(timedelta(days=1))

    job = fetch_github_summary_post_to_slack.queue(channel_name, boundary_dt)

    task = PostGitHubSummaryTask(
        job_id=job.id,
        name="Post GitHub Summary",
        description="Daily task to post GitHub Summary",
        user=task_owner,
        data={"channel_name": channel_name, "boundary_dt": boundary_dt.isoformat()},
    )
    db.session.add(task)
    db.session.commit()


@rq.job
def fetch_github_summary_post_to_slack(channel_name, boundary_dt):
    channel_info = slack.get_channel_info(channel_name)
    users: List[User] = User.query.filter(
        and_(User.slack_id.in_(channel_info.members), User.github_username.isnot(None))
    ).all()
    random.shuffle(users)

    message = ""
    num_users = len(users)
    for idx, user in enumerate(users):
        logger.info("[Busy-Beaver] Compiling stats for {0}".format(user))
        user_events = GitHubUserEvents(user, boundary_dt)
        message += user_events.generate_summary_text()
        set_task_progress(idx / (num_users + 1) * 100)

    if not message:
        message = (
            '"If code falls outside version control, and no one is around to read it, '
            'does it make a sound?" - Zax Rosenberg'
        )

    slack.post_message(message=message, channel_id=channel_info.id)
    set_task_progress(100)
