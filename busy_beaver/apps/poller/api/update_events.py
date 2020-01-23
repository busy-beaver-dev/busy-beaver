import logging

from flask import request
from flask.views import MethodView

from busy_beaver.apps.events_database.task import start_sync_event_database_task
from busy_beaver.common.decorators import admin_role_required
from busy_beaver.toolbox import make_response

logger = logging.getLogger(__name__)


class AddEventPollingResource(MethodView):
    """Endpoint to trigger polling of Meetup for events to add to database"""

    decorators = [admin_role_required]

    def post(self):
        user = request._internal["user"]
        logger.info(
            "[Busy Beaver] Add New Events Poll -- login successful",
            extra={"user": user.username},
        )

        start_sync_event_database_task(user)

        logger.info("[Busy Beaver] Add New Events Poll -- kicked-off")
        return make_response(200, json={"run": "complete"})
