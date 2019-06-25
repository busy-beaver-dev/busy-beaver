import logging

from flask import request
from flask.views import MethodView

from busy_beaver.apps.github_summary.task import start_post_github_summary_task
from busy_beaver.blueprints.decorators import admin_role_required
from busy_beaver.toolbox import make_response

logger = logging.getLogger(__name__)


class PublishGitHubSummaryResource(MethodView):
    """Endpoint to trigger process of creating and publishing GitHub Summary to Slack"""

    decorators = [admin_role_required]

    def post(self):
        user = request._internal["user"]
        logger.info(
            "[Busy Beaver] Post GitHub Summary Request -- login successful",
            extra={"user": user.username},
        )

        # TODO: replace this with marshmallow
        # Get workspace_id and pass it into github_summary task
        data = request.json
        if not data or "channel" not in data or "workspace_id" not in data:
            logger.error("[Busy Beaver] Post GitHub Summary Task -- channel in body")
            return make_response(
                status_code=422,
                error={"message": "JSON requires both 'channel'and 'workspace_id' key"},
            )
        start_post_github_summary_task(user, data["workspace_id"], data["channel"])

        logger.info("[Busy Beaver] Post GitHub Summary -- kicked-off")
        return make_response(200, json={"run": "complete"})
