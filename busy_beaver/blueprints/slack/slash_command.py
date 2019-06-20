import functools
import logging
from typing import List, NamedTuple
from urllib.parse import urlencode
import uuid

from flask import request
from flask.views import MethodView

from .toolbox import make_slack_response
from busy_beaver.apps.upcoming_events.workflow import (
    generate_next_event_message,
    generate_upcoming_events_message,
)
from busy_beaver.config import (
    FULL_INSTALLATION_WORKSPACE_IDS,
    GITHUB_CLIENT_ID,
    GITHUB_REDIRECT_URI,
    MEETUP_GROUP_NAME,
)
from busy_beaver.extensions import db
from busy_beaver.models import User
from busy_beaver.toolbox import EventEmitter

logger = logging.getLogger(__name__)
slash_command_dispatcher = EventEmitter()

ACCOUNT_ALREADY_ASSOCIATED = (
    "You have already associated a GitHub account with your Slack handle. "
    "Please use `/busybeaver reconnect` to link to a different account."
)
NO_ASSOCIATED_ACCOUNT = (
    "No associated account. Use `/busybeaver connect` to link your account."
)
VERIFY_ACCOUNT = (
    "Follow the link below to validate your GitHub account. "
    "I'll reference your GitHub username to track your public activity."
)
HELP_TEXT = (
    "`/busybeaver next`\t\t Retrieve next event\n"
    "`/busybeaver events`\t\t Retrieve list of upcoming event\n"
    "`/busybeaver connect`\t\t Connect GitHub Account\n"
    "`/busybeaver reconnect`\t\t Connect to difference GitHub Account\n"
    "`/busybeaver disconnect`\t\t Disconenct GitHub Account\n"
    "`/busybeaver help`\t\t Display help text"
)


class Command(NamedTuple):
    type: str
    args: List[str]


class SlackSlashCommandDispatchResource(MethodView):
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


############
# Decorators
############
def limit_to(workspace_ids: List[str]):

    if not isinstance(workspace_ids, list):
        raise ValueError

    def limit_to_decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            team_id = kwargs["team_id"]
            if team_id not in workspace_ids:
                return make_slack_response(text="Command not supported at this time.")

            return func(*args, **kwargs)

        return _wrapper

    return limit_to_decorator


#########################
# Upcoming Event Schedule
#########################
@limit_to(workspace_ids=FULL_INSTALLATION_WORKSPACE_IDS)
@slash_command_dispatcher.on("next")
def next_event(**data):
    attachment = generate_next_event_message(MEETUP_GROUP_NAME)
    return make_slack_response(attachments=attachment)


@limit_to(workspace_ids=FULL_INSTALLATION_WORKSPACE_IDS)
@slash_command_dispatcher.on("events")
def upcoming_events(**data):
    blocks = generate_upcoming_events_message(MEETUP_GROUP_NAME, count=5)
    return make_slack_response(blocks=blocks)


########################
# Miscellaneous Commands
########################
@slash_command_dispatcher.on("help")
def display_help_text(**data):
    # have 2 different help text phrases
    return make_slack_response(text=HELP_TEXT)


@slash_command_dispatcher.on("not_found")
def command_not_found(**data):
    logger.info("[Busy Beaver] Unknown command")
    return make_slack_response(text="Command not found. Try `/busybeaver help`")


##########################################
# Associate GitHub account with Slack user
# TODO refactor this
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
    user = User.query.filter_by(slack_id=slack_id).first()

    if not user:
        logger.info("[Busy Beaver] Slack acount does not have associated GitHub")
        return make_slack_response(text=NO_ASSOCIATED_ACCOUNT)

    user = add_tracking_identifer_and_save_record(user)
    attachment = create_github_account_attachment(user.github_state)
    return make_slack_response(text=VERIFY_ACCOUNT, attachments=attachment)


@slash_command_dispatcher.on("disconnect")
def disconnect_github(**data):
    logger.info("[Busy Beaver] Disconnecting GitHub account.")
    slack_id = data["user_id"]
    user = User.query.filter_by(slack_id=slack_id).first()

    if not user:
        logger.info("[Busy Beaver] Slack acount does not have associated GitHub")
        return make_slack_response(text="No GitHub account associated with profile")

    db.session.delete(user)
    db.session.commit()
    return make_slack_response(
        text="Account has been deleted. `/busybeaver connect` to reconnect"
    )


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
