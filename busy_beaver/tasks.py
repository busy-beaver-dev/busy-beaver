from datetime import timedelta
import logging
from typing import List

from sqlalchemy import and_

from . import api, db, github_stats, slack
from .models import User
from .toolbox import utc_now_minus

logger = logging.getLogger(__name__)


@api.background.task
def post_github_summary_to_slack(channel: str) -> None:
    boundary_dt = utc_now_minus(timedelta(days=1))
    channel_id = slack.get_channel_id(channel)
    members = slack.get_channel_members(channel_id)

    users: List[User] = db.query(User).filter(
        and_(User.slack_id.in_(members), User.github_username.isnot(None))
    ).all()
    message = ""
    for user in users:
        logger.info("[Busy-Beaver] Compiling stats for {0}".format(user))
        message += github_stats.generate_summary(user, boundary_dt)

    slack.post_message(channel_id, message)
