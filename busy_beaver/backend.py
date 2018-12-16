import os
import logging
import time
from urllib.parse import urlencode
import uuid

import requests

from . import api, db
from .models import User
from .adapters.slack import SlackAdapter

logger = logging.getLogger(__name__)

CLIENT_ID = os.getenv("GITHUB_APP_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_APP_CLIENT_SECRET")
GITHUB_REDIRECT_URI = "https://busybeaver.sivji.com/github-integration"
SLACK_CALLBACK_URI = "https://busybeaver.sivji.com/slack-event-subscription"

SLACK_TOKEN = os.getenv("SLACK_BOTUSER_OAUTH_TOKEN")
slack = SlackAdapter(SLACK_TOKEN)


#########
# Sandbox
#########
@api.background.task
def debug(s=2, *, data):
    time.sleep(s)
    # import pdb; pdb.set_trace()
    print("slept!")


class HelloWorldResource:
    """For testing purposes"""

    def on_get(self, req, resp):
        logger.info("[Busy-Beaver] Hit hello world endpoint", extra={"test": "payload"})
        resp.media = {"Hello": "World"}


api.add_route("/hello", HelloWorldResource())


#######
# Slack
#######
class SlackEventSubscriptionResource:
    async def on_post(self, req, resp):
        data = await req.media()

        verification_request = data["type"] == "url_verification"
        if verification_request:
            resp.media = {"challenge": data["challenge"]}
            return

        event = data["event"]
        msg_from_bot = event.get("subtype") == "bot_message"
        if event["type"] == "message" and msg_from_bot:
            return

        dm_to_bot = event["channel_type"] == "im"
        if event["type"] == "message" and dm_to_bot:
            reply_to_user_with_github_login_link(event)


api.add_route("/slack-event-subscription", SlackEventSubscriptionResource())

SEND_LINK_COMMANDS = ["link me"]
RESEND_LINK_COMMANDS = ["link me again"]
ALL_LINK_COMMANDS = SEND_LINK_COMMANDS + RESEND_LINK_COMMANDS

UNKNOWN_COMMAND_MSG = "Don't recognize your command. Type `link me` link your GitHub."
ACCOUNT_ALREADY_ASSOCIATED_MSG = (
    "You have already associated a GitHub account with your Slack handle. "
    "Please type `link me again` to link to a different account."
)

@api.background.task
def reply_to_user_with_github_login_link(event):
    chat_text = str.lower(event["text"])
    slack_id = event["user"]
    channel = event["channel"]

    if chat_text not in ALL_LINK_COMMANDS:
        slack.post_message(channel, UNKNOWN_COMMAND_MSG)
        return

    user_record = db.query(User).filter_by(slack_id=slack_id).first()
    if user_record and chat_text in SEND_LINK_COMMANDS:
        slack.post_message(channel, ACCOUNT_ALREADY_ASSOCIATED_MSG)
        return

    # generate unique identifer to track user during authentication process
    state = str(uuid.uuid4())
    if user_record and chat_text in RESEND_LINK_COMMANDS:
        user_record.github_state = state
        db.session.add(user_record)
        db.session.commit()
    if not user_record:
        user = User()
        user.slack_id = slack_id
        user.github_state = state

        db.session.add(user)
        db.session.commit()

    data = {"client_id": CLIENT_ID, "redirect_uri": GITHUB_REDIRECT_URI, "state": state}
    query_params = urlencode(data)
    url = f"https://github.com/login/oauth/authorize?{query_params}"
    slack.post_message(channel, url)
    return


########
# GitHub
########
class GitHubIntegrationResource:
    def on_get(self, req, resp):
        params = req.params
        code = params.get("code")
        state = params.get("state")

        user = db.query(User).filter_by(github_state=state).first()
        if not user:
            return {"Error": "Unknown"}

        exchange_code_for_access_token(code, state, user)
        resp.media = {"Login": "successful"}


api.add_route("/github-integration", GitHubIntegrationResource())


def exchange_code_for_access_token(code, state, user):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "state": state,
    }

    headers = {"Accept": "application/json"}

    resp = requests.post(
        "https://github.com/login/oauth/access_token", data=data, headers=headers
    )

    body = resp.json()
    access_token = body["access_token"]

    # use access token to get user details (another function)

    headers = {"Accept": "application/json", "Authorization": f"token {access_token}"}
    resp = requests.get("https://api.github.com/user", headers=headers)
    body = resp.json()

    # add to user record in database (with access_token)
    user.github_id = body["id"]
    user.github_username = body["login"]
    user.github_state = None
    user.github_access_token = access_token

    db.session.add(user)
    db.session.commit()
