from typing import List, NamedTuple

from slackclient import SlackClient


class Channel(NamedTuple):
    name: str
    id: str
    members: List[str] = None


class TimezoneInfo(NamedTuple):
    tz: str
    label: str
    offset: int


class SlackAdapter:
    def __init__(self, slack_token):
        self.sc = SlackClient(slack_token)

    def dm(self, message, user_id):
        return self.post_message(message, channel_id=user_id, as_user=True)

    def get_channel_info(self, channel_name) -> Channel:
        channel_id = self._get_channel_id(channel_name)
        members = self._get_channel_members(channel_id)
        return Channel(channel_name, channel_id, members)

    def get_user_timezone(self, user_id):
        result = self.sc.api_call("users.info", user=user_id, include_locale=True)
        return TimezoneInfo(
            tz=result["user"]["tz"],
            label=result["user"]["tz_label"],
            offset=result["user"]["tz_offset"],
        )

    def post_ephemeral_message(self, message, channel_id, user_id):
        return self.sc.api_call(
            "chat.postEphemeral",
            text=message,
            channel=channel_id,
            user=user_id,
            attachments=None,
        )

    def post_message(
        self,
        message="",
        *,
        blocks=None,
        attachments=None,
        channel=None,
        channel_id=None,
        unfurl_links=True,
        unfurl_media=True,
        as_user=False,
    ):
        if not channel and not channel_id:
            raise ValueError("Must specify channel or channel_id")

        if not channel_id:
            channel_id = self._get_channel_id(channel)
        return self.sc.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            blocks=blocks,
            attachments=attachments,
            unfurl_links=unfurl_links,
            unfurl_media=unfurl_media,
            as_user=as_user,
        )

    def _get_channel_id(self, channel_name: str) -> str:
        channels = self._get_all_channels()
        return [t.id for t in channels if t.name == channel_name][0]

    def _get_channel_members(self, channel_id: str) -> List[str]:
        channel_info = self.sc.api_call("channels.info", channel=channel_id)
        return channel_info["channel"]["members"]

    def _get_all_channels(self):
        channels = self.sc.api_call("channels.list")
        return [Channel(c["name"], c["id"]) for c in channels["channels"]]
