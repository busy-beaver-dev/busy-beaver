import logging

from flask import request
from flask.views import MethodView

from .decorators import slack_verification_required
from busy_beaver.apps.slack_integration.event_subscription import (
    process_event_subscription_callback,
)

logger = logging.getLogger(__name__)


class SlackEventSubscriptionResource(MethodView):
    """Callback endpoint for Slack event subscriptions"""

    decorators = [slack_verification_required]

    def post(self):
        data = request.json
        logger.info("Received event from Slack", extra={"request_json": data})
        return process_event_subscription_callback(data)
