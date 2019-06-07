import logging

from flask import jsonify, request
from flask.views import MethodView

from busy_beaver.exceptions import UnverifiedWebhookRequest
from busy_beaver.toolbox import EventEmitter

logger = logging.getLogger(__name__)
github_event_dispatcher = EventEmitter()


class GitHubEventSubscriptionResource(MethodView):
    """Callback endpoint for GitHub event subscriptions"""

    def post(self):
        data = request.json
        logger.info("[Busy Beaver] Received GitHub event", extra={"req_json": data})

        event_type = request.headers.get("X-GitHub-Event", None)
        if not event_type:
            return UnverifiedWebhookRequest("Missing GitHub event type")

        github_event_dispatcher.emit(event_type, default="ping", data=data)
        return jsonify(True)


@github_event_dispatcher.on("ping")
def handle_ping(data):
    pass


@github_event_dispatcher.on("pr")  # TODO
def handle_pr(data):
    pass


@github_event_dispatcher.on("issue")  # TODO
def handle_issue(data):
    pass
