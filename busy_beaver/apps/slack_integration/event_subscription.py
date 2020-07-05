import logging

from .blocks import AppHome
from .slash_command import HELP_TEXT
from busy_beaver.apps.slack_integration.oauth.state_machine import (
    SlackInstallationOnboardUserWorkflow,
)
from busy_beaver.apps.slack_integration.oauth.workflow import (
    GITHUB_SUMMARY_CHANNEL_JOIN_MESSAGE,
)
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.config import FULL_INSTALLATION_WORKSPACE_IDS, MEETUP_GROUP_NAME
from busy_beaver.extensions import db
from busy_beaver.models import GitHubSummaryConfiguration, SlackInstallation, SlackUser
from busy_beaver.toolbox import EventEmitter

logger = logging.getLogger(__name__)
subscription_dispatch = EventEmitter()
event_dispatch = EventEmitter()


def process_event_subscription_callback(data):
    return subscription_dispatch.emit(data["type"], default="not_found", data=data)


#######################
# Subscription Handlers
#######################
@subscription_dispatch.on("app_uninstalled")  # TODO
@subscription_dispatch.on("not_found")
@event_dispatch.on("not_found")
def command_not_found(data):
    logger.info("[Busy Beaver] Unknown command")
    return None


@subscription_dispatch.on("url_verification")
def url_verification_handler(data):
    logger.info("[Busy Beaver] Slack -- API Verification")
    return {"challenge": data["challenge"]}


@subscription_dispatch.on("event_callback")
def event_callback_dispatcher(data):
    logger.info("[Busy Beaver] Slack -- Event Callback")
    return event_dispatch.emit(data["event"]["type"], default="not_found", data=data)


################
# Event Handlers
################
@event_dispatch.on("message")
def message_handler(data):
    event = data["event"]
    if event.get("bot_id") or event.get("subtype") == "bot_message":
        return None

    user_messages_bot = event["channel_type"] == "im"
    if user_messages_bot:
        params = {"workspace_id": data["team_id"]}
        installation = SlackInstallation.query.filter_by(**params).first()

        bot_recieves_configuration_information = (
            installation.state == "config_requested"
            and installation.authorizing_user_id == event["user"]
        )
        if bot_recieves_configuration_information:
            entered_time = event["text"]
            workflow = SlackInstallationOnboardUserWorkflow(
                installation, payload=entered_time
            )
            workflow.advance()
            return None

        logger.info("[Busy Beaver] Slack -- Unknown command")
        slack = SlackClient(installation.bot_access_token)
        slack.post_message(HELP_TEXT, channel=data["event"]["channel"])

    return None


@event_dispatch.on("member_joined_channel")
def member_joined_channel_handler(data):
    workspace_id = data["team_id"]
    user_id = data["event"]["user"]
    channel = data["event"]["channel"]

    installation = SlackInstallation.query.filter_by(workspace_id=workspace_id).first()
    bot_invited_to_channel = user_id == installation.bot_user_id
    if bot_invited_to_channel:
        github_summary_configured = installation.github_summary_config
        if not github_summary_configured:
            github_summary_config = GitHubSummaryConfiguration(channel=channel)
            github_summary_config.slack_installation = installation
            db.session.add(github_summary_config)
            db.session.commit()

            db.session.refresh(installation)
            workflow = SlackInstallationOnboardUserWorkflow(installation)
            workflow.advance()
        else:
            # bot was invited to a different channel
            # TODO add to table of channels for that workspace
            pass

        return None

    user_joins_github_summary_channel = (
        installation.github_summary_config.channel == channel
        and installation.state == "active"
    )
    if user_joins_github_summary_channel:
        slack = SlackClient(installation.bot_access_token)
        slack.post_ephemeral_message(
            GITHUB_SUMMARY_CHANNEL_JOIN_MESSAGE.format(channel=channel),
            channel=channel,
            user_id=user_id,
        )

    return None


@event_dispatch.on("app_home_opened")
def app_home_handler(data):
    """Display App Home

    Currently we do show first-time viewers a separate screen... should we?
    """
    logger.info("app_home_opened Event", extra=data)
    workspace_id = data["team_id"]
    user_id = data["event"]["user"]
    tab_opened = data["event"]["tab"]

    if tab_opened != "home":
        return None

    installation = SlackInstallation.query.filter_by(workspace_id=workspace_id).first()
    params = {"installation_id": installation.id, "slack_id": user_id}
    user = SlackUser.query.filter_by(**params).first()
    if not user:
        logger.info("First app_home_opened for user", extra=data)
        user = SlackUser(**params)
        user.app_home_opened_count = 0

    user.app_home_opened_count += 1
    db.session.add(user)
    db.session.commit()

    # TODO would be smart to use the state machine to figure out what to post
    github_summary_configured = installation.github_summary_config
    if github_summary_configured:
        channel = installation.github_summary_config.channel
        if workspace_id in FULL_INSTALLATION_WORKSPACE_IDS:
            app_home = AppHome(channel=channel, meetup_group=MEETUP_GROUP_NAME)
        else:
            app_home = AppHome(channel=channel)
    else:
        app_home = AppHome()

    slack = SlackClient(installation.bot_access_token)
    slack.display_app_home(user_id, view=app_home.to_dict())
    return None
