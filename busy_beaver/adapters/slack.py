from typing import List, NamedTuple

from slack import WebClient


class Channel(NamedTuple):
    name: str
    members: List[str] = None


class TimezoneInfo(NamedTuple):
    tz: str
    label: str
    offset: int


class SlackClient:
    def __init__(self, slack_token):
        self.client = WebClient(slack_token, run_async=False)

    def __repr__(self):  # pragma: no cover
        return "<SlackClient>"

    def dm(self, message, user_id):
        return self.post_message(message, channel=user_id)

    def get_channel_info(self, channel) -> Channel:
        channel_info = self.client.channels_info(channel=channel)
        members = channel_info["channel"]["members"]
        return Channel(channel, members)

    def get_channel_list(self, *, include_members=False):
        exclude_members = not include_members
        return self.client.channels_list(exclude_members=int(exclude_members))

    def get_user_timezone(self, user_id):
        result = self.client.users_info(user=user_id)
        return TimezoneInfo(
            tz=result["user"]["tz"],
            label=result["user"]["tz_label"],
            offset=result["user"]["tz_offset"],
        )

    def post_ephemeral_message(self, message, channel, user_id):
        return self.client.chat_postEphemeral(
            text=message, channel=channel, user=user_id, attachments=None
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
    ):
        if not channel:
            raise ValueError("Must specify channel")

        return self.client.chat_postMessage(
            channel=channel,
            text=message,
            blocks=blocks,
            attachments=attachments,
            unfurl_links=unfurl_links,
            unfurl_media=unfurl_media,
        )

    def display_app_home(self, user_id, view):
        return self.client.views_publish(user_id=user_id, view=view)
