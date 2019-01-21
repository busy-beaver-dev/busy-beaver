import logging
import os

import requests

from .. import db
from ..models import User

logger = logging.getLogger(__name__)

CLIENT_ID = os.getenv("GITHUB_APP_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_APP_CLIENT_SECRET")
GITHUB_REDIRECT_URI = "https://busybeaver.sivji.com/github-integration"


class GitHubIdentityVerificationCallbackResource:
    """Callback endpoint to verify GitHub username

    In order to link Slack IDs to GitHub usernames, we have to create a GitHub OAuth App
    with a callback URL that GitHub can send verification messages to once user connect
    their account.
    """

    def on_get(self, req, resp):
        logger.info("[Busy-Beaver] GitHub Redirect")
        params = req.params
        code = params.get("code")
        state = params.get("state")

        user = db.query(User).filter_by(github_state=state).first()
        if not user:
            logger.error("[Busy-Beaver] GitHub state does not match")
            return {"Error": "Unknown"}

        exchange_code_for_access_token(code, state, user)
        logger.info("[Busy-Beaver] Account is linked to GitHub")
        resp.media = {"Login": "successful"}


def exchange_code_for_access_token(code, state, user):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "state": state,
    }

    headers = {"Accept": "application/json"}

    logger.info("[Busy-Beaver] Changing code for OAuth token")
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
