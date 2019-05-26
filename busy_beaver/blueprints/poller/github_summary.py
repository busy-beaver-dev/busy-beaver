import logging

from flask import request
from flask.views import MethodView

from busy_beaver.tasks import start_post_github_summary_task
from busy_beaver.toolbox import make_response

logger = logging.getLogger(__name__)


class PublishGitHubSummaryResource(MethodView):
    """Endpoint to trigger process of creating and publishing GitHub Summary to Slack
    """

    def post(self):
        user = request._internal["user"]
        logger.info(
            "[Busy Beaver] Post GitHub Summary Request -- login successful",
            extra={"user": user.username},
        )

        # TODO: replace this with marshmallow
        data = request.json
        if not data or "channel" not in data:
            logger.error("[Busy Beaver] Post GitHub Summary Task -- channel in body")
            return make_response(422, error={"message": "JSON requires 'channel' key"})
        start_post_github_summary_task(user, data["channel"])

        logger.info("[Busy Beaver] Post GitHub Summary -- kicked-off")
        return make_response(200, json={"run": "complete"})
