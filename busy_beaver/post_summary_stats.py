import os
from typing import List

from . import api, db, github_stats
from .adapters.slack import SlackAdapter
from .models import User

from sqlalchemy import and_

slack_token = os.getenv("SLACK_BOTUSER_OAUTH_TOKEN")
slack = SlackAdapter(slack_token)


@api.background.task
def post_summary(channel: str) -> None:
    channel_id = get_channel_id(channel)
    members = get_channel_members(channel_id)

    text = ""
    users: List[User] = db.query(User).filter(
        and_(User.slack_id.in_(members)), User.github_username.isnot(None)
    ).all()
    for user in users:
        text += github_stats.recent_activity_text(user)

    slack.post_message(channel_id, text)


def get_channel_id(channel_name):
    channels = slack.get_channels()
    return [t.id_ for t in channels if t.name == channel_name][0]


def get_channel_members(channel_id: str) -> List[str]:
    channel_info = slack.get_channel_info(channel_id)
    return channel_info["channel"]["members"]
