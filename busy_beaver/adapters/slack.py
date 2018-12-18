from typing import NamedTuple

from slackclient import SlackClient


class Channel(NamedTuple):
    id_: str
    name: str


class SlackAdapter:
    def __init__(self, slack_token):
        self.sc = SlackClient(slack_token)

    def get_channels(self):
        channels = self.sc.api_call("channels.list")
        return [
            Channel(channel["id"], channel["name"]) for channel in channels["channels"]
        ]

    def get_channel_info(self, channel_id):
        return self.sc.api_call("channels.info", channel=channel_id)

    def post_message(self, channel, text, attachments=None):
        return self.sc.api_call(
            "chat.postMessage", channel=channel, text=text, attachments=attachments
        )
