import logging
from typing import List, NamedTuple
from urllib.parse import urlencode
import uuid
from flask import request
from flask.views import MethodView
from .decorators import limit_to, slack_verification_required
from .toolbox import make_slack_response
from busy_beaver.apps.upcoming_events.workflow import (
    generate_next_event_message,
    generate_upcoming_events_message,
)
from busy_beaver.apps.github_summary.workflow import (generate_account_attachment, delete_account_attachment)
from busy_beaver.config import (
    FULL_INSTALLATION_WORKSPACE_IDS,
    GITHUB_CLIENT_ID,
    GITHUB_REDIRECT_URI,
    MEETUP_GROUP_NAME,
)
from busy_beaver.extensions import db
from busy_beaver.models import GitHubSummaryUser, SlackInstallation
from busy_beaver.toolbox import EventEmitter

logger = logging.getLogger(__name__)
slash_command_dispatcher = EventEmitter()

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

    decorators = [slack_verification_required]

    def post(self):
        data = dict(request.form)
        command = self.parse_command_text(data["text"])
        return slash_command_dispatcher.emit(command.type, default="not_found", **data)

    def parse_command_text(self, command_text: str) -> Command:
        command_parts = command_text.split()
        if not command_parts:
            return Command(type="not_found", args=[])
        return Command(command_parts[0].lower(), args=command_parts[1:])


#########################
# Upcoming Event Schedule
#########################
@slash_command_dispatcher.on("next")
@limit_to(workspace_ids=FULL_INSTALLATION_WORKSPACE_IDS)
def next_event(**data):
    attachment = generate_next_event_message(MEETUP_GROUP_NAME)
    return make_slack_response(attachments=attachment)


@slash_command_dispatcher.on("events")
@limit_to(workspace_ids=FULL_INSTALLATION_WORKSPACE_IDS)
def upcoming_events(**data):
    blocks = generate_upcoming_events_message(MEETUP_GROUP_NAME, count=5)
    return make_slack_response(blocks=blocks)


########################
# Miscellaneous Commands
########################
@slash_command_dispatcher.on("help")
def display_help_text(**data):
    return make_slack_response(text=HELP_TEXT)


@slash_command_dispatcher.on("not_found")
def command_not_found(**data):
    logger.info("[Busy Beaver] Unknown command")
    return make_slack_response(text="Command not found. Try `/busybeaver help`")


@slash_command_dispatcher.on("connect")
def link_github(**data):
    logger.info("[Busy Beaver] Slash command to associate with Github account.")
    message, attachment = generate_account_attachment(**data)
    return make_slack_response(text=message, attachments=attachment)


@slash_command_dispatcher.on("reconnect")
def relink_github(**data):
    logger.info("[Busy Beaver] Slash command to relink GitHub account.")
    message, attachment = generate_account_attachment(**data)
    return make_slack_response(text=message, attachments=attachment)


@slash_command_dispatcher.on("disconnect")
def disconnect_github(**data):
    logger.info("[Busy Beaver] Disconnecting GitHub account.")
    message = delete_account_attachment(**data)
    return make_slack_response(text=message)


def add_tracking_identifer_and_save_record(user: GitHubSummaryUser) -> None:
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
