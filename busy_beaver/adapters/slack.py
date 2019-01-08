from typing import List, NamedTuple

from slackclient import SlackClient


class SlackAdapter:
    def __init__(self, slack_token):
        self.sc = SlackClient(slack_token)

    def get_channel_id(self, channel_name: str) -> str:
        channels = self._get_channels()
        return [t.id_ for t in channels if t.name == channel_name][0]

    def get_channel_members(self, channel_id: str) -> List[str]:
        channel_info = self._get_channel_info(channel_id)
        return channel_info["channel"]["members"]

    def post_message(self, channel, text, attachments=None):
        return self.sc.api_call(
            "chat.postMessage", channel=channel, text=text, attachments=attachments
        )

    def _get_channels(self):
        channels = self.sc.api_call("channels.list")
        return [
            Channel(channel["id"], channel["name"]) for channel in channels["channels"]
        ]

    def _get_channel_info(self, channel_id):
        return self.sc.api_call("channels.info", channel=channel_id)


class Channel(NamedTuple):
    id_: str
    name: str
