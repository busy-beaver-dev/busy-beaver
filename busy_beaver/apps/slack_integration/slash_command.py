import logging
from typing import List, NamedTuple

from .interactors import generate_help_text, make_slack_response
from .models import SlackInstallation, SlackUser
from busy_beaver.apps.github_integration.oauth.workflow import (
    connect_github_to_slack,
    disconnect_github_from_slack,
    relink_github_to_slack,
)
from busy_beaver.apps.slack_integration.oauth.workflow import (
    create_link_to_login_to_settings,
)
from busy_beaver.apps.upcoming_events.upcoming_events import (
    generate_next_event_message,
    generate_upcoming_events_message,
)
from busy_beaver.extensions import db
from busy_beaver.toolbox import EventEmitter

logger = logging.getLogger(__name__)
slash_command_dispatcher = EventEmitter()


class Command(NamedTuple):
    type: str
    args: List[str]


def process_slash_command(data):
    command = _parse_command(data["text"])
    workspace = data["team_id"]
    user_id = data["user_id"]

    installation = SlackInstallation.query.filter_by(workspace_id=workspace).first()
    if not installation:
        raise ValueError("workspace not found")

    user = SlackUser.query.filter_by(
        slack_id=user_id, installation=installation
    ).first()
    if not user:
        user = SlackUser()
        user.slack_id = user_id
        user.installation = installation
        db.session.add(user)
        db.session.commit()

    data["installation"] = installation
    data["user"] = user
    return slash_command_dispatcher.emit(command.type, default="not_found", **data)


def _parse_command(command_text: str) -> Command:
    command_parts = command_text.split()
    if not command_parts:
        return Command(type="not_found", args=[])
    return Command(command_parts[0].lower(), args=command_parts[1:])


def create_url_attachment(url, text):
    if url:
        return {
            "fallback": url,
            "attachment_type": "default",
            "actions": [{"text": text, "type": "button", "url": url}],
        }
    return None


#########################
# Upcoming Event Schedule
#########################
@slash_command_dispatcher.on("next")
def next_event(**data):
    installation = data["installation"]
    upcoming_events_config = installation.upcoming_events_config
    if not upcoming_events_config:
        return make_slack_response(text="Feature not configured.")
    if not upcoming_events_config.enabled:
        return make_slack_response(text="This feature has been disabled.")

    attachment = generate_next_event_message(upcoming_events_config)
    return make_slack_response(attachments=attachment)


@slash_command_dispatcher.on("events")
def upcoming_events(**data):
    installation = data["installation"]
    upcoming_events_config = installation.upcoming_events_config
    if not upcoming_events_config:
        return make_slack_response(text="Feature not configured.")
    if not upcoming_events_config.enabled:
        return make_slack_response(text="This feature has been disabled.")

    blocks = generate_upcoming_events_message(upcoming_events_config)
    return make_slack_response(blocks=blocks)


########################
# Miscellaneous Commands
########################
@slash_command_dispatcher.on("help")
def display_help_text(**data):
    installation = data["installation"]
    help_text = generate_help_text(installation)
    return make_slack_response(text=help_text)


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
    slack_user = data["user"]
    installation = data["installation"]

    text, url = connect_github_to_slack(installation, slack_user)
    attachment = create_url_attachment(url, text="Associate GitHub Profile")
    return make_slack_response(text=text, attachments=attachment)


@slash_command_dispatcher.on("reconnect")
def relink_github(**data):
    logger.info("Relinking GitHub account", extra=data)
    slack_user = data["user"]
    installation = data["installation"]

    text, url = relink_github_to_slack(installation, slack_user)
    attachment = create_url_attachment(url, text="Associate GitHub Profile")
    return make_slack_response(text=text, attachments=attachment)


@slash_command_dispatcher.on("disconnect")
def disconnect_github(**data):
    logger.info("Disconnecting GitHub account.")
    slack_user = data["user"]
    installation = data["installation"]

    text, _ = disconnect_github_from_slack(installation, slack_user)
    return make_slack_response(text=text)


#############################
# Access Busy Beaver Settings
#############################
@slash_command_dispatcher.on("settings")
def login_to_busy_beaver_settings(**data):
    logger.info("Requested settings url", extra=data)
    slack_user = data["user"]

    text, url = create_link_to_login_to_settings(slack_user)
    attachment = create_url_attachment(url, text="Login to Access Settings")
    return make_slack_response(text=text, attachments=attachment)
