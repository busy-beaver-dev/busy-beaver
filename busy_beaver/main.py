import os

from .adapters.slack import SlackAdapter
from .github_stats import recent_activity_text

slack_token = os.environ["SLACK_API_TOKEN"]
slack = SlackAdapter(slack_token)


def post_update(channel):
    channels = slack.get_channels()
    channel_id = [t.id_ for t in channels if t.name == "busybeaver_test"][0]

    channel_info = slack.get_channel_info(channel_id)
    channel_members = channel_info["channel"]["members"]  # noqa

    # TODO Get GitHub username from database
    usernames = ["alysivji", "chrisluedtke"]

    text = ""
    for user in usernames:
        text += recent_activity_text(user)

    slack.post_message(channel_id, text)
