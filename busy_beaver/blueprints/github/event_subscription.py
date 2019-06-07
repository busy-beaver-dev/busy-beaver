import logging

from flask import jsonify, request
from flask.views import MethodView

logger = logging.getLogger(__name__)


class GitHubEventSubscriptionResource(MethodView):
    """Callback endpoint for GitHub event subscriptions"""

    def post(self):
        data = request.json
        logger.info("[Busy Beaver] Received GitHub event", extra={"req_json": data})

        # TODO eventemitter on header... X-GitHub-Event: ping
        return jsonify(True)
