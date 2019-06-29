import logging

from flask import jsonify, request
from flask.views import MethodView

from .decorators import slack_verification_required
from .slash_command import HELP_TEXT
from busy_beaver import chipy_slack
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
    if event.get("bot_id"):
        logger.info("[Busy Beaver] Slack -- Bot messaging user")
        return jsonify(None)
    if event.get("subtype") == "bot_message":
        logger.info("[Busy Beaver] Slack -- Bot gets its own DM")
        return jsonify(None)
    if event["channel_type"] == "im":
        logger.info("[Busy Beaver] Slack -- Unknown command")
        chipy_slack.post_message(HELP_TEXT, channel_id=data["event"]["channel"])
    return jsonify(None)


@event_dispatch.on("member_joined_channel")
def member_joined_channel_handler(data):
    # workspace_id = data["team_id"]
    # user_id = data["event"]["user"]
    # channel_id = data["event"]["channel"]

    # slack_installation
    # if user matches my id
    # if the team and channel are something i know about
    return jsonify(None)
