from datetime import datetime, timedelta
import logging
import os
from typing import List

from sqlalchemy import and_
import pytz

from .. import api, db, github_stats
from ..adapters.slack import SlackAdapter
from ..models import ApiUser, User

logger = logging.getLogger(__name__)

SLACK_TOKEN = os.getenv("SLACK_BOTUSER_OAUTH_TOKEN")
slack = SlackAdapter(SLACK_TOKEN)


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


@api.background.task
def post_github_summary_to_slack(channel: str) -> None:
    boundary_dt = utc_now_minus(timedelta(days=1))
    channel_id = slack.get_channel_id(channel)
    members = slack.get_channel_members(channel_id)

    users: List[User] = db.query(User).filter(
        and_(User.slack_id.in_(members), User.github_username.isnot(None))
    ).all()
    message = ""
    for user in users:
        message += github_stats.generate_summary(user, boundary_dt)

    slack.post_message(channel_id, message)


def utc_now_minus(period: timedelta):
    return pytz.utc.localize(datetime.utcnow()) - period
