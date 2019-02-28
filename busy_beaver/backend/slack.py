import logging
import os
from urllib.parse import urlencode
import uuid

from .. import api, db, slack
from ..models import User

logger = logging.getLogger(__name__)

CLIENT_ID = os.getenv("GITHUB_APP_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_APP_CLIENT_SECRET")
GITHUB_REDIRECT_URI = "https://busybeaver.sivji.com/github-integration"

SEND_LINK_COMMANDS = ["connect"]
RESEND_LINK_COMMANDS = ["reconnect"]
ALL_LINK_COMMANDS = SEND_LINK_COMMANDS + RESEND_LINK_COMMANDS

UNKNOWN_COMMAND = (
    "I don't recognize your command. Type `connect` to link your GitHub account."
)
ACCOUNT_ALREADY_ASSOCIATED = (
    "You have already associated a GitHub account with your Slack handle. "
    "Please type `reconnect` to link to a different account."
)
VERIFY_ACCOUNT = (
    "Follow the link below to validate your GitHub account. "
    "I'll reference your GitHub username to track your public activity."
)


class SlackEventSubscriptionResource:
    """Callback endpoint for Slack event subscriptions

    TODO: refactor to make more modular and readable, bot makes minimal use of slack
    event subscriptions; low priority
    """

    async def on_post(self, req, resp):
        data = await req.media()
        logger.info("[Busy-Beaver] Recieved event from Slack", extra={"req_json": data})

        verification_request = data["type"] == "url_verification"
        if verification_request:
            logger.info("[Busy-Beaver] Slack -- API Verification")
            resp.media = {"challenge": data["challenge"]}
            return

        # bot can see its own DMs
        event = data["event"]
        msg_from_bot = event.get("subtype") == "bot_message"
        if event["type"] == "message" and msg_from_bot:
            return

        dm_to_bot = event["channel_type"] == "im"
        if event["type"] == "message" and dm_to_bot:
            reply_to_user_with_github_login_link(event)


@api.background.task
def reply_to_user_with_github_login_link(event):
    chat_text = str.lower(event["text"])
    slack_id = event["user"]
    channel_id = event["channel"]

    if chat_text not in ALL_LINK_COMMANDS:
        logger.info("[Busy-Beaver] Unknown command")
        slack.post_message(UNKNOWN_COMMAND, channel_id=channel_id)
        return

    user_record = db.query(User).filter_by(slack_id=slack_id).first()
    if user_record and chat_text in SEND_LINK_COMMANDS:
        logger.info("[Busy-Beaver] Slack acount already linked to GitHub")
        slack.post_message(ACCOUNT_ALREADY_ASSOCIATED, channel_id=channel_id)
        return

    # generate unique identifer to track user during authentication process
    state = str(uuid.uuid4())
    if user_record and chat_text in RESEND_LINK_COMMANDS:
        logger.info("[Busy-Beaver] Relinking GitHub account.")
        user_record.github_state = state
        db.session.add(user_record)
        db.session.commit()
    if not user_record:
        logger.info("[Busy-Beaver] New user. Linking GitHub account.")
        user = User()
        user.slack_id = slack_id
        user.github_state = state

        db.session.add(user)
        db.session.commit()

    data = {"client_id": CLIENT_ID, "redirect_uri": GITHUB_REDIRECT_URI, "state": state}
    query_params = urlencode(data)
    url = f"https://github.com/login/oauth/authorize?{query_params}"
    attachment = [
        {
            "fallback": url,
            "attachment_type": "default",
            "actions": [
                {"text": "Associate GitHub Profile", "type": "button", "url": url}
            ],
        }
    ]
    slack.post_message(VERIFY_ACCOUNT, channel_id=channel_id, attachments=attachment)
    return
