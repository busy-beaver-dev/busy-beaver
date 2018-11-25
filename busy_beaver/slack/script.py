import os

from slackclient import SlackClient

from busy_beaver.userstats.script import recent_activity_text

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)


def post_update():
    channels = sc.api_call("channels.list")
    channels = [(channel['id'], channel['name']) for channel in channels['channels']]
    channel_id = [t[0] for t in channels if t[1] == 'busybeaver_test'][0]

    channel_info = sc.api_call(
          "channels.info",
          channel=channel_id
    )

    channel_members = channel_info['channel']['members']  # noqa

    # TODO Get GitHub username from database
    usernames = ['alysivji', 'chrisluedtke']

    text = ""

    for user in usernames:
        text += recent_activity_text(user)

    sc.api_call(
        "chat.postMessage",
        channel=channel_id,
        text=text
    )
