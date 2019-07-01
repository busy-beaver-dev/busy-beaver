from typing import List, NamedTuple

from slackclient import SlackClient


class Channel(NamedTuple):
    name: str
    members: List[str] = None


class TimezoneInfo(NamedTuple):
    tz: str
    label: str
    offset: int


class SlackAdapter:
    def __init__(self, slack_token):
        self.sc = SlackClient(slack_token)

    def dm(self, message, user_id):
        return self.post_message(message, channel=user_id, as_user=True)

    def get_channel_info(self, channel) -> Channel:
        members = self._get_channel_members(channel)
        return Channel(channel, members)

    def get_user_timezone(self, user_id):
        result = self.sc.api_call("users.info", user=user_id, include_locale=True)
        return TimezoneInfo(
            tz=result["user"]["tz"],
            label=result["user"]["tz_label"],
            offset=result["user"]["tz_offset"],
        )

    def post_ephemeral_message(self, message, channel, user_id):
        return self.sc.api_call(
            "chat.postEphemeral",
            text=message,
            channel=channel,
            user=user_id,
            attachments=None,
        )

    def post_message(
        self,
        message="",
        channel=None,
        *,
        blocks=None,
        attachments=None,
        unfurl_links=True,
        unfurl_media=True,
        as_user=False,
    ):
        if not channel:
            raise ValueError("Must specify channel")

        return self.sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=message,
            blocks=blocks,
            attachments=attachments,
            unfurl_links=unfurl_links,
            unfurl_media=unfurl_media,
            as_user=as_user,
        )

    def _get_channel_members(self, channel: str) -> List[str]:
        channel_info = self.sc.api_call("channels.info", channel=channel)
        return channel_info["channel"]["members"]
