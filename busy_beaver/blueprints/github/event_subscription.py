import logging

from flask import jsonify, request
from flask.views import MethodView

from .decorators import github_verification_required
from busy_beaver.apps.github_webhook.event_subscription import (
    process_github_event_subscription,
)
from busy_beaver.exceptions import UnverifiedWebhookRequest
from busy_beaver.toolbox import EventEmitter

logger = logging.getLogger(__name__)
github_event_dispatcher = EventEmitter()


class GitHubEventSubscriptionResource(MethodView):
    """Callback endpoint for GitHub event subscriptions"""

    decorators = [github_verification_required]

    def post(self):
        data = request.json
        logger.info("Received GitHub event", extra={"request_json": data})

        event_type = request.headers.get("X-GitHub-Event", None)
        if not event_type:
            raise UnverifiedWebhookRequest("Missing GitHub event type")

        return jsonify(process_github_event_subscription(event_type, data))
