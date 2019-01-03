from datetime import datetime, timedelta
from typing import List
import os

from sqlalchemy import and_
import pytz

from . import api, db, github_stats
from .adapters.slack import SlackAdapter
from .models import User

slack_token = os.getenv("SLACK_BOTUSER_OAUTH_TOKEN")
slack = SlackAdapter(slack_token)


@api.background.task
def post_summary(channel: str) -> None:
    boundary_dt = utc_now_minus(timedelta(days=1))
    channel_id = get_channel_id(channel)
    members = get_channel_members(channel_id)

    users: List[User] = db.query(User).filter(
        and_(User.slack_id.in_(members), User.github_username.isnot(None))
    ).all()
    message = ""
    for user in users:
        message += github_stats.generate_summary(user, boundary_dt)

    slack.post_message(channel_id, message)


def get_channel_id(channel_name):
    channels = slack.get_channels()
    return [t.id_ for t in channels if t.name == channel_name][0]


def get_channel_members(channel_id: str) -> List[str]:
    channel_info = slack.get_channel_info(channel_id)
    return channel_info["channel"]["members"]


def utc_now_minus(period: timedelta):
    return pytz.utc.localize(datetime.utcnow()) - period
