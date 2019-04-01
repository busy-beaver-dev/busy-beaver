import logging

from flask import request
from flask.views import MethodView

from busy_beaver.config import TWITTER_USERNAME
from busy_beaver.tasks.retweeter import post_tweets_to_slack
from busy_beaver.toolbox import make_response

logger = logging.getLogger(__name__)


class TwitterPollingResource(MethodView):
    """Endpoint to trigger polling of Twitter for new tweets to post to channel
    """

    def post(self):
        user = request._internal["user"]
        logger.info(
            "[Busy-Beaver] Twitter Summary Poll -- login successful",
            extra={"user": user.username},
        )

        # TODO need to add a task queue here
        data = request.json
        if "channel" not in data:
            logger.error(
                "[Busy-Beaver] Twitter Summary Poll -- need channel in JSON body"
            )
            return
        post_tweets_to_slack(username=TWITTER_USERNAME, channel=data["channel"])

        logger.info("[Busy-Beaver] Twitter Summary Poll -- kicked-off")
        return make_response(200, json={"run": "complete"})
