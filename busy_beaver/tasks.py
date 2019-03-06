from datetime import timedelta
import logging
from typing import List

from sqlalchemy import and_

from . import github_stats, slack
from .models import User
from .toolbox import utc_now_minus

logger = logging.getLogger(__name__)


def post_github_summary_to_slack(channel: str) -> None:
    boundary_dt = utc_now_minus(timedelta(days=1))
    channel_info = slack.get_channel_info(channel)

    users: List[User] = User.query.filter(
        and_(User.slack_id.in_(channel_info.members), User.github_username.isnot(None))
    ).all()
    message = ""
    for user in users:
        logger.info("[Busy-Beaver] Compiling stats for {0}".format(user))
        message += github_stats.generate_summary(user, boundary_dt)

    if not message:
        message = (
            '"If code falls outside version control, and no one is around to read it, '
            'does it make a sound?" - Zax Rosenberg'
        )

    slack.post_message(message, channel_id=channel_info.id)
