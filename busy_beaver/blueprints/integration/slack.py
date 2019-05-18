import logging
from typing import List, NamedTuple
from urllib.parse import urlencode
import uuid

from flask import jsonify, request
from flask.views import MethodView

from busy_beaver import meetup, slack
from busy_beaver.config import GITHUB_CLIENT_ID, GITHUB_REDIRECT_URI
from busy_beaver.extensions import db
from busy_beaver.models import User
from busy_beaver.toolbox import EventEmitter, make_slack_response

logger = logging.getLogger(__name__)
slash_command_dispatcher = EventEmitter()

SEND_LINK_COMMANDS = ["connect"]
RESEND_LINK_COMMANDS = ["reconnect"]
ALL_LINK_COMMANDS = SEND_LINK_COMMANDS + RESEND_LINK_COMMANDS

UNKNOWN_COMMAND = (
    "I don't recognize your command. Type `connect` to link your GitHub account."
)
ACCOUNT_ALREADY_ASSOCIATED = (
    "You have already associated a GitHub account with your Slack handle. "
    "Please use `/busybeaver reconnect` to link to a different account."
)
NO_ASSOCIATED_ACCOUNT = (
    "No associated account. Please use `/busybeaver connect` to link your account."
)
VERIFY_ACCOUNT = (
    "Follow the link below to validate your GitHub account. "
    "I'll reference your GitHub username to track your public activity."
)
BOT_RESPONSE_TO_SLASH = "Find all available Busy Beaver Commands using /busybeaver help"


class SlackEventSubscriptionResource(MethodView):
    """Callback endpoint for Slack event subscriptions"""

    def post(self):
        data = request.json
        logger.info("[Busy Beaver] Received event from Slack", extra={"req_json": data})

        verification_request = data["type"] == "url_verification"
        if verification_request:
            logger.info("[Busy Beaver] Slack -- API Verification")
            return jsonify({"challenge": data["challenge"]})

        # bot can see its own DMs
        event = data["event"]
        msg_from_bot = event.get("subtype") == "bot_message"
        if event["type"] == "message" and msg_from_bot:
            return jsonify(None)

        dm_to_bot = event["channel_type"] == "im"
        if event["type"] == "message" and dm_to_bot:
            slack.post_message(BOT_RESPONSE_TO_SLASH, channel_id=event["channel"])
        return jsonify(None)


class Command(NamedTuple):
    type: str
    args: List[str]


class SlackSlashCommandDispatcher(MethodView):
    """Dealing with slash commands"""

    def post(self):
        data = dict(request.form)
        command = self.parse_command_text(data["text"])
        return slash_command_dispatcher.emit(command.type, default="not_found", **data)

    def parse_command_text(self, command_text: str) -> Command:
        command_parts = command_text.split()
        if not command_parts:
            return Command(type="not_found", args=[])
        return Command(command_parts[0].lower(), args=command_parts[1:])


##########################################
# Associate GitHub account with Slack user
##########################################
@slash_command_dispatcher.on("connect")
def link_github(**data):
    logger.info("[Busy Beaver] New user. Linking GitHub account.")
    slack_id = data["user_id"]
    user_record = User.query.filter_by(slack_id=slack_id).first()

    if user_record:
        logger.info("[Busy Beaver] Slack acount already linked to GitHub")
        return make_slack_response(text=ACCOUNT_ALREADY_ASSOCIATED)

    user = User()
    user.slack_id = slack_id
    user = add_tracking_identifer_and_save_record(user)
    attachment = create_github_account_attachment(user.github_state)
    return make_slack_response(text=VERIFY_ACCOUNT, attachments=attachment)


@slash_command_dispatcher.on("reconnect")
def relink_github(**data):
    logger.info("[Busy Beaver] Relinking GitHub account.")
    slack_id = data["user_id"]
    user_record = User.query.filter_by(slack_id=slack_id).first()

    if not user_record:
        logger.info("[Busy Beaver] Slack acount does not have associated GitHub")
        return make_slack_response(text=NO_ASSOCIATED_ACCOUNT)

    user = add_tracking_identifer_and_save_record(user_record)
    attachment = create_github_account_attachment(user.github_state)
    return make_slack_response(text=VERIFY_ACCOUNT, attachments=attachment)


def add_tracking_identifer_and_save_record(user: User) -> None:
    user.github_state = str(uuid.uuid4())  # generate unique identifer to track user
    db.session.add(user)
    db.session.commit()
    return user


def create_github_account_attachment(state):

    data = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "state": state,
    }
    query_params = urlencode(data)
    url = f"https://github.com/login/oauth/authorize?{query_params}"
    return {
        "fallback": url,
        "attachment_type": "default",
        "actions": [{"text": "Associate GitHub Profile", "type": "button", "url": url}],
    }


#########################
# Upcoming Event Schedule
#########################
@slash_command_dispatcher.on("next")
def next_event(**data):
    event = meetup.get_events(count=1)[0]
    attachment = create_next_event_attachment(event)
    return make_slack_response(attachments=attachment)


def create_next_event_attachment(event: dict) -> dict:
    """Make a Slack attachment for the event."""
    if "venue" in event:
        venue_name = event["venue"]["name"]
    else:
        venue_name = "TBD"

    return {
        "mrkdwn_in": ["text", "pretext"],
        "pretext": "*Next ChiPy Event:*",
        "title": event["name"],
        "title_link": event["event_url"],
        "fallback": "{}: {}".format(event["name"], event["event_url"]),
        "text": "*<!date^{}^{{time}} {{date_long}}|no date>* at {}".format(
            int(event["time"] / 1000), venue_name
        ),
        "color": "#008952",
    }


########################
# Miscellaneous Commands
########################
@slash_command_dispatcher.on("help")
def display_help_text(**data):
    return make_slack_response(
        text="/busybeaver next to upcoming event /busybeaver help to see help text"
    )


@slash_command_dispatcher.on("not_found")
def command_not_found(**data):
    logger.info("[Busy Beaver] Unknown command")
    return make_slack_response(text="Command not found")
