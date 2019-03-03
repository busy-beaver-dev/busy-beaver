import logging
from busy_beaver.decorators import authentication_required
from busy_beaver.tasks import post_github_summary_to_slack

logger = logging.getLogger(__name__)


class PublishGitHubSummaryResource:
    """Endpoint to trigger process of creating and publishing GitHub Summary to Slack
    """

    @authentication_required
    async def on_post(self, req, resp, user):
        logger.info(
            "[Busy-Beaver] Post GitHub Summary Request -- login successful",
            extra={"user": user.username},
        )

        # TODO need to add a task queue here
        data = await req.media()
        if "channel" not in data:
            logger.error(
                "[Busy-Beaver] Post GitHub Summary Request -- ",
                "need channel in JSON body",
            )
            return
        post_github_summary_to_slack(data["channel"])

        logger.info("[Busy-Beaver] Post GitHub Summary -- kicked-off")
        resp.media = {"run": "kicked_off"}
