import os
import time
from urllib.parse import urlencode
import uuid

import requests
import responder

from . import db
from .models import User
from .adapters.slack import SlackAdapter

CLIENT_ID = os.getenv("GITHUB_APP_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_APP_CLIENT_SECRET")
REDIRECT_URI = "http://2263c64a.ngrok.io/github-integration"

SLACK_TOKEN = os.getenv("SLACK_API_TOKEN")
slack = SlackAdapter(SLACK_TOKEN)

api = responder.API()


@api.background.task
def debug(s=2, *, data):
    time.sleep(s)
    # import pdb; pdb.set_trace()
    print("slept!")


#######
# Slack
#######
class SlackEventSubscriptionResource:
    async def on_post(self, req, resp):
        data = await req.media()

        if data["type"] == "url_verification":
            resp.media = {"challenge": data["challenge"]}
            return

        event = data["event"]
        if event["type"] == "message" and event.get("subtype") == "bot_message":
            return
        if event["type"] == "message" and event["channel_type"] == "im":
            reply_to_user_with_github_login_link(event)

        # debug(2, data=data)


api.add_route("/slack-event-subscription", SlackEventSubscriptionResource())


@api.background.task
def reply_to_user_with_github_login_link(event):
    chat_text = str.lower(event["text"])
    print(event)
    slack_id = event["user"]
    print(event)
    # channel

    if "link me" not in chat_text:
        print("didn't say the magic words")
        return

    user_record = db.query(User).filter_by(slack_id=slack_id).first()
    if user_record:
        # TODO send message
        print("already exists")
        return

    # generate unique identifer to track user during authentication process
    state = str(uuid.uuid4())

    user = User()
    user.slack_id = slack_id
    user.github_state = state

    print(user)

    db.session.add(user)
    db.session.commit()

    data = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": state,
    }
    query_params = urlencode(data)
    url = f"https://github.com/login/oauth/authorize?{query_params}"
    slack.post_message(event["channel"], url)


########
# GitHub
########
class GitHubIntegrationResource:
    async def on_get(self, req, resp):
        params = req.params
        code = params["code"]
        state = params["state"]

        print("here")
        print(state)
        print(code)

        user = db.query(User).filter_by(github_state=state).first()
        if not user:
            return {"Error": "Unknown"}

        exchange_code_for_access_token(code, state, user)
        print("here")
        resp.media = {"Login": "successful"}


api.add_route("/github-integration", GitHubIntegrationResource())


# @api.background.task
def exchange_code_for_access_token(code, state, user):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "state": state,
    }

    headers = {
        "Accept": "application/json"
    }

    resp = requests.post("https://github.com/login/oauth/access_token", data=data, headers=headers)

    body = resp.json()
    access_token = body["access_token"]

    # use access token to get user details (another function)

    headers = {
        "Accept": "application/json",
        "Authorization": f"token {access_token}"
    }
    resp = requests.get("https://api.github.com/user", headers=headers)
    body = resp.json()

    print(user.github_id)
    # add to user record in database (with access_token)
    user.github_id = body["id"]
    user.github_state = None
    user.github_access_token = access_token

    db.session.add(user)
    db.session.commit()
