import logging
from typing import List, NamedTuple

from slack import WebClient
from slack.errors import SlackApiError

from busy_beaver.exceptions import SlackTooManyBlocks

logger = logging.getLogger()


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

    def channel_details(self, channel):
        try:
            result = self.client.conversations_info(channel=channel)
        except SlackApiError:
            raise ValueError("Channel not found")
        return result["channel"]

    def get_channel_members(self, channel) -> List[str]:
        try:
            result = self.client.conversations_members(channel=channel)
        except SlackApiError:
            raise ValueError("Channel not found")
        return result["members"]

    def get_bot_channels(self) -> List[str]:
        result = self.client.users_conversations()
        all_bot_channels = [
            (channel["id"], channel["name"]) for channel in result["channels"]
        ]
        return sorted(all_bot_channels, key=lambda record: record[1])

    def is_admin(self, user_id):
        try:
            result = self.client.users_info(user=user_id)
        except SlackApiError:
            raise ValueError("User not found")
        return result["user"]["is_admin"]

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

        # can have a max of 50 blocks for message
        # can have a max of 100 blocks in modal and home tab
        if blocks:
            if len(blocks) > 50:
                raise SlackTooManyBlocks()

        try:
            result = self.client.chat_postMessage(
                channel=channel,
                text=message,
                blocks=blocks,
                attachments=attachments,
                unfurl_links=unfurl_links,
                unfurl_media=unfurl_media,
            )
        except SlackApiError as exc:
            response = exc.response
            extra = {
                "status_code": response.status_code,
                "response_body": response.data,
            }
            logger.exception("FAILED posting message to slack", extra=extra)

            error = response.data["error"]
            if error == "channel_not_found":
                raise ValueError("Channel not found")
            elif error == "not_in_channel":
                raise ValueError("Not in channel")
            elif error == "invalid_blocks":
                raise ValueError("Invalid blocks")
            raise ValueError("Unknown error")

        return result

    def display_app_home(self, user_id, view):
        # TODO check size of view
        return self.client.views_publish(user_id=user_id, view=view)
