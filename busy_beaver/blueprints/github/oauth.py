import logging

from flask import jsonify, request
from flask.views import MethodView

from busy_beaver.adapters import RequestsClient
from busy_beaver.config import (
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_REDIRECT_URI,
)
from busy_beaver.extensions import db
from busy_beaver.models import GitHubSummaryUser

logger = logging.getLogger(__name__)
client = RequestsClient()


class GitHubIdentityVerificationCallbackResource(MethodView):
    """Callback endpoint to verify GitHub username

    In order to link Slack IDs to GitHub usernames, we have to create a GitHub OAuth App
    with a callback URL that GitHub can send verification messages to once user connect
    their account.
    """

    def get(self):
        logger.info("[Busy Beaver] GitHub Redirect")
        params = request.args
        code = params.get("code")
        state = params.get("state")

        user = GitHubSummaryUser.query.filter_by(github_state=state).first()
        if not user:
            logger.error("[Busy Beaver] GitHub state does not match")
            return jsonify({"Error": "Unknown"})

        exchange_code_for_access_token(code, state, user)
        logger.info("[Busy Beaver] Account is linked to GitHub")
        return jsonify({"Login": "successful"})


def exchange_code_for_access_token(code, state, user):
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "state": state,
    }

    logger.info("[Busy Beaver] Changing code for OAuth token")
    resp = client.post("https://github.com/login/oauth/access_token", json=data)
    access_token = resp.json["access_token"]

    # use access token to get user details (another function)
    headers = {"Authorization": f"token {access_token}"}
    resp = client.get("https://api.github.com/user", headers=headers)

    # add to user record in database (with access_token)
    user.github_id = resp.json["id"]
    user.github_username = resp.json["login"]
    user.github_state = None
    user.github_access_token = access_token

    db.session.add(user)
    db.session.commit()
