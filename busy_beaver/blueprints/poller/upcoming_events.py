import logging

from flask import request
from flask.views import MethodView

from busy_beaver.apps.upcoming_events.workflow import (
    post_upcoming_events_message_to_slack,
)
from busy_beaver.toolbox import make_response

logger = logging.getLogger(__name__)


class PublishUpcomingEventsResource(MethodView):
    """Endpoint to trigger posting of Upcoming Events to Slack"""

    def post(self):
        user = request._internal["user"]
        logger.info(
            "[Busy Beaver] Post Upcoming Events -- login successful",
            extra={"user": user.username},
        )

        # TODO: replace this with marshmallow
        data = request.json
        if not data or "channel" not in data:
            logger.error(
                "[Busy Beaver] Post Upcoming Events -- need channel in JSON body"
            )
            return make_response(422, error={"message": "JSON requires 'channel' key"})
        post_upcoming_events_message_to_slack(
            channel=data["channel"], group_name="ChiPy", count=5
        )

        logger.info("[Busy Beaver] Post Upcoming Events -- complete")
        return make_response(200, json={"run": "complete"})
