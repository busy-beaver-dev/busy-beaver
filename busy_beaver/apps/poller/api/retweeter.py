import logging

from flask import request
from flask.views import MethodView

from busy_beaver.apps.retweeter.task import start_post_tweets_to_slack_task
from busy_beaver.common.decorators import admin_role_required
from busy_beaver.toolbox import make_response

logger = logging.getLogger(__name__)


class TwitterPollingResource(MethodView):
    """Endpoint to trigger polling of Twitter for new tweets to post to channel"""

    decorators = [admin_role_required]

    def post(self):
        user = request._internal["user"]
        logger.info(
            "[Busy Beaver] Twitter Summary Poll -- login successful",
            extra={"user": user.username},
        )

        # TODO: replace this with marshmallow
        # Get workspace_id and pass it into task
        # for now we can hack it so we only use chipy_slack for this
        data = request.json
        if not data or "channel" not in data:
            logger.error(
                "[Busy Beaver] Twitter Summary Poll -- need channel in JSON body"
            )
            return make_response(422, error={"message": "JSON requires 'channel' key"})
        start_post_tweets_to_slack_task(user, channel_name=data["channel"])

        logger.info("[Busy Beaver] Twitter Summary Poll -- kicked-off")
        return make_response(200, json={"run": "complete"})
