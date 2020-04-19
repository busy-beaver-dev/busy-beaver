import logging
from typing import List, NamedTuple

from .decorators import limit_to
from .toolbox import make_slack_response
from busy_beaver.apps.events.workflow import (
    generate_next_event_message,
    generate_upcoming_events_message,
)
from busy_beaver.apps.github_integration.oauth.workflow import (
    connect_github_to_slack,
    disconnect_github_from_slack,
    relink_github_to_slack,
)
from busy_beaver.config import FULL_INSTALLATION_WORKSPACE_IDS, MEETUP_GROUP_NAME
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


def process_slash_command(data):
    command = _parse_command(data["text"])
    return slash_command_dispatcher.emit(command.type, default="not_found", **data)


def _parse_command(command_text: str) -> Command:
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


##########################################
# Associate GitHub account with Slack user
##########################################
@slash_command_dispatcher.on("connect")
def link_github(**data):
    logger.info("Linking GitHub account for new user", extra=data)
    slack_id = data["user_id"]
    workspace_id = data["team_id"]

    text, url = connect_github_to_slack(slack_id, workspace_id)
    attachment = create_github_account_attachment(url)
    return make_slack_response(text=text, attachments=attachment)


@slash_command_dispatcher.on("reconnect")
def relink_github(**data):
    logger.info("Relinking GitHub account", extra=data)
    slack_id = data["user_id"]
    workspace_id = data["team_id"]

    text, url = relink_github_to_slack(slack_id, workspace_id)
    attachment = create_github_account_attachment(url)
    return make_slack_response(text=text, attachments=attachment)


@slash_command_dispatcher.on("disconnect")
def disconnect_github(**data):
    logger.info("Disconnecting GitHub account.")
    slack_id = data["user_id"]
    workspace_id = data["team_id"]

    text, _ = disconnect_github_from_slack(slack_id, workspace_id)
    return make_slack_response(text=text)


def create_github_account_attachment(url=None):
    if url:
        return {
            "fallback": url,
            "attachment_type": "default",
            "actions": [
                {"text": "Associate GitHub Profile", "type": "button", "url": url}
            ],
        }
    return None
