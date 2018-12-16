import os
from typing import List

from . import github_stats
from .adapters.slack import SlackAdapter

from . import db
from .models import User

slack_token = os.environ["SLACK_BOTUSER_OAUTH_TOKEN"]
slack = SlackAdapter(slack_token)


def get_channel_id(channel_name):
    channels = slack.get_channels()
    return [t.id_ for t in channels if t.name == channel_name][0]


def get_channel_members(channel_id: str) -> List[str]:
    channel_info = slack.get_channel_info(channel_id)
    return channel_info["channel"]["members"]


def post_update(channel: str) -> None:
    channel_id = get_channel_id(channel)
    members = get_channel_members(channel_id)

    text = ""
    github_usernames: List[User] = db.query(User).filter(User.slack_id.in_(members))
    for user in github_usernames:
        text += github_stats.recent_activity_text(user.github_username)

    slack.post_message(channel_id, text)
