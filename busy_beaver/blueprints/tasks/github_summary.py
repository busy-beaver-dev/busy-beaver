import logging

from flask import request
from flask.views import MethodView

from busy_beaver.tasks import post_github_summary_to_slack
from busy_beaver.toolbox import make_response

logger = logging.getLogger(__name__)


class PublishGitHubSummaryResource(MethodView):
    """Endpoint to trigger process of creating and publishing GitHub Summary to Slack
    """

    def post(self):
        user = request._internal["user"]
        logger.info(
            "[Busy-Beaver] Post GitHub Summary Request -- login successful",
            extra={"user": user.username},
        )

        # TODO need to add a task queue here
        data = request.json
        if "channel" not in data:
            logger.error("[Busy-Beaver] Post GitHub Summary Task -- channel in body")
            return
        post_github_summary_to_slack(data["channel"])

        logger.info("[Busy-Beaver] Post GitHub Summary -- kicked-off")
        return make_response(200, json={"run": "complete"})
