import logging

from flask import jsonify, request
from flask.views import MethodView

from .decorators import slack_verification_required
from .slash_command import HELP_TEXT
from busy_beaver import chipy_slack
from busy_beaver.adapters import SlackAdapter
from busy_beaver.extensions import db
from busy_beaver.models import GitHubSummaryConfiguration, SlackInstallation
from busy_beaver.sandbox.state_machine_spike import OnboardUserWorkflow
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

    # user messages bot
    if event["channel_type"] == "im":
        i = SlackInstallation.query.filter_by(workspace_id=data["team_id"]).first()
        if (i.state == "config_requested") and (i.authorizing_user_id == event["user"]):
            # grab time and restart throw it into the state machine
            entered_time = event["text"]
            workflow = OnboardUserWorkflow(i, payload=entered_time)
            workflow.advance()
        else:
            logger.info("[Busy Beaver] Slack -- Unknown command")
            chipy_slack.post_message(HELP_TEXT, channel_id=data["event"]["channel"])

    return jsonify(None)


@event_dispatch.on("member_joined_channel")
def member_joined_channel_handler(data):
    workspace_id = data["team_id"]
    user_id = data["event"]["user"]
    channel_id = data["event"]["channel"]

    installation = SlackInstallation.query.filter_by(workspace_id=workspace_id).first()
    if user_id == installation.bot_user_id:
        # bot was invited to channel
        if not installation.github_summary_config:
            github_summary_config = GitHubSummaryConfiguration(channel=channel_id)
            github_summary_config.slack_installation = installation
            db.session.add(github_summary_config)
            db.session.commit()

            db.session.refresh(installation)
            workflow = OnboardUserWorkflow(installation)
            workflow.advance()
        else:
            # bot was invited to a different channel
            # TODO add to table of channels for that workspace
            pass

        return jsonify(None)

    # TODO only if we are active once this is active
    if channel_id == installation.github_summary_config.channel_id:
        slack = SlackAdapter(installation.bot_access_token)
        slack.dm(user_id, "thx for joining")

    return jsonify(None)
