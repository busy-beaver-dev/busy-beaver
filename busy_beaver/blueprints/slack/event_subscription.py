import logging

from flask import jsonify, request
from flask.views import MethodView

from .decorators import slack_verification_required
from .slash_command import HELP_TEXT
from busy_beaver.adapters import SlackAdapter
from busy_beaver.apps.external_integrations.state_machine import (
    SlackInstallationOnboardUserWorkflow,
)
from busy_beaver.extensions import db
from busy_beaver.models import GitHubSummaryConfiguration, SlackInstallation
from busy_beaver.toolbox import EventEmitter

logger = logging.getLogger(__name__)
subscription_dispatch = EventEmitter()
event_dispatch = EventEmitter()


class SlackEventSubscriptionResource(MethodView):
    """Callback endpoint for Slack event subscriptions"""

    decorators = [slack_verification_required]

    def post(self):
        data = request.json
        logger.info("[Busy Beaver] Received event from Slack", extra={"req_json": data})
        return subscription_dispatch.emit(data["type"], default="not_found", data=data)


#######################
# Subscription Handlers
#######################
@subscription_dispatch.on("app_uninstalled")  # TODO
@subscription_dispatch.on("not_found")
@event_dispatch.on("not_found")
def command_not_found(data):
    logger.info("[Busy Beaver] Unknown command")
    return jsonify(None)


@subscription_dispatch.on("url_verification")
def url_verification_handler(data):
    logger.info("[Busy Beaver] Slack -- API Verification")
    return jsonify({"challenge": data["challenge"]})


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
        return jsonify(None)

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
            return jsonify(None)

        logger.info("[Busy Beaver] Slack -- Unknown command")
        slack = SlackAdapter(installation.bot_access_token)
        slack.post_message(HELP_TEXT, channel_id=data["event"]["channel"])

    return jsonify(None)


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

        return jsonify(None)

    user_joins_github_summary_channel = (
        installation.github_summary_config.channel == channel
        and installation.state == "active"
    )
    if user_joins_github_summary_channel:
        slack = SlackAdapter(installation.bot_access_token)
        slack.post_ephemeral_message(
            "thx for joining", channel_id=channel, user_id=user_id
        )

    return jsonify(None)
