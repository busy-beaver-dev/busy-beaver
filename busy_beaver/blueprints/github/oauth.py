import logging

from flask import jsonify, request
from flask.views import MethodView

from busy_beaver.apps.oauth_integrations.github.workflow import (
    process_github_oauth_callback,
)

logger = logging.getLogger(__name__)


class GitHubIdentityVerificationCallbackResource(MethodView):
    """Callback endpoint to verify GitHub username

    In order to link Slack IDs to GitHub usernames, we have to create a GitHub OAuth App
    with a callback URL that GitHub can send verification messages to once user connect
    their account.
    """

    def get(self):
        logger.info("GitHub OAuth Callback")
        params = request.args
        code = params.get("code")
        state = params.get("state")
        callback_url = request.url

        result = process_github_oauth_callback(callback_url, state, code)
        return jsonify(result)
