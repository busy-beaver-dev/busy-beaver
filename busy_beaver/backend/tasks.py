import logging

from .. import db
from ..models import ApiUser
from ..tasks import post_github_summary_to_slack

logger = logging.getLogger(__name__)


class PublishGitHubSummaryResource:
    """Endpoint to trigger process of creating and publishing GitHub Summary to Slack
    """

    async def on_post(self, req, resp):
        logger.info("[Busy-Beaver] Post GitHub Summary Request")

        if "authorization" not in req.headers:
            logger.error("[Busy-Beaver] Post GitHub Summary Request -- no auth header")
            resp.status_code = 401
            resp.media = {"message": "Include header: Authorization: 'token {token}'"}
            return

        token = req.headers["authorization"].split("token ")[1]
        api_user: ApiUser = db.query(ApiUser).filter_by(token=token).first()
        if not api_user:
            logger.error("[Busy-Beaver] Invalid token")
            resp.status_code = 401
            resp.media = {"message": "Invalid token, please talk to admin"}
            return

        # TODO maybe add a task queue here
        logger.info(
            "[Busy-Beaver] Post GitHub Summary Request -- login successful",
            extra={"api_user": api_user.username},
        )
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
