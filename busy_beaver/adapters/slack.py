from typing import List, NamedTuple

from slackclient import SlackClient


class Channel(NamedTuple):
    id: str
    name: str
    members: List[str] = None


class SlackAdapter:
    def __init__(self, slack_token):
        self.sc = SlackClient(slack_token)

    def get_channel_info(self, channel) -> Channel:
        channel_id = self._get_channel_id(channel)
        members = self._get_channel_members(channel_id)
        return Channel(channel_id, channel, members)

    def post_message(self, message, *, attachments=None, channel=None, channel_id=None):
        if not channel and not channel_id:
            raise ValueError("Must specify channel or channel_id")

        if not channel_id:
            channel_id = self._get_channel_id(channel)
        return self.sc.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            attachments=attachments,
        )

    def _get_channel_id(self, channel_name: str) -> str:
        channels = self._get_all_channels()
        return [t.id for t in channels if t.name == channel_name][0]

    def _get_channel_members(self, channel_id: str) -> List[str]:
        channel_info = self.sc.api_call("channels.info", channel=channel_id)
        return channel_info["channel"]["members"]

    def _get_all_channels(self):
        channels = self.sc.api_call("channels.list")
        return [Channel(c["id"], c["name"]) for c in channels["channels"]]
