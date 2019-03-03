import logging
from busy_beaver.config import TWITTER_USERNAME
from busy_beaver.decorators import authentication_required
from busy_beaver.retweeter import post_tweets_to_slack

logger = logging.getLogger(__name__)


class TwitterPollingResource:
    """Endpoint to trigger polling of Twitter for new tweets to post to channel
    """

    @authentication_required
    async def on_post(self, req, resp, user):
        logger.info(
            "[Busy-Beaver] Twitter Summary Poll -- login successful",
            extra={"user": user.username},
        )

        # TODO maybe add a task queue here
        data = await req.media()
        if "channel" not in data:
            logger.error(
                "[Busy-Beaver] Twitter Summary Poll -- need channel in JSON body",
            )
            return
        post_tweets_to_slack(username=TWITTER_USERNAME, channel=data["channel"])

        logger.info("[Busy-Beaver] Twitter Summary Poll -- kicked-off")
        resp.media = {"run": "kicked_off"}
