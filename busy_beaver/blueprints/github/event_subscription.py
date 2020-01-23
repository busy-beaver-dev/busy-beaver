import logging

from flask import jsonify, request
from flask.views import MethodView

from .decorators import github_verification_required
from busy_beaver.apps.github_webhook.workflow import (
    generate_new_issue_message,
    generate_new_pull_request_message,
)
from busy_beaver.clients import chipy_slack
from busy_beaver.exceptions import UnverifiedWebhookRequest
from busy_beaver.toolbox import EventEmitter

logger = logging.getLogger(__name__)
github_event_dispatcher = EventEmitter()


class GitHubEventSubscriptionResource(MethodView):
    """Callback endpoint for GitHub event subscriptions"""

    decorators = [github_verification_required]

    def post(self):
        data = request.json
        logger.info("[Busy Beaver] Received GitHub event", extra={"req_json": data})

        event_type = request.headers.get("X-GitHub-Event", None)
        if not event_type:
            raise UnverifiedWebhookRequest("Missing GitHub event type")

        github_event_dispatcher.emit(event_type, default="not_found", data=data)
        return jsonify(True)


@github_event_dispatcher.on("not_found")
@github_event_dispatcher.on("ping")
def do_nothing(data):
    pass


@github_event_dispatcher.on("issues")
def handle_issue(data):
    message = generate_new_issue_message(data)
    if message:
        _post_to_slack(message)


@github_event_dispatcher.on("pull_request")
def handle_pr(data):
    message = generate_new_pull_request_message(data)
    if message:
        _post_to_slack(message)


@github_event_dispatcher.on("release")
def handle_release(data):
    message = generate_new_pull_request_message(data)
    if message:
        _post_to_slack(message)


def _post_to_slack(message):
    chipy_slack.post_message(message=message, channel="busy-beaver-meta")
