import logging

from flask import jsonify, redirect, request, url_for
from flask.views import MethodView
from flask_login import login_user

from busy_beaver.apps.slack_integration.oauth.workflow import (
    process_slack_installation_callback,
    process_slack_sign_in_callback,
    send_welcome_message,
)

logger = logging.getLogger(__name__)


class SlackAppInstallationCallbackResource(MethodView):
    """Callback endpoint for installing app into Slack workspace"""

    def get(self):
        logger.info("Slack Workspace Installation")
        callback_url = request.url
        installation = process_slack_installation_callback(callback_url)
        send_welcome_message(installation)
        # TODO take them an actual page
        return jsonify({"Installation": "successful"})


class SlackSignInCallbackResource(MethodView):
    """Callback endpoint for Sign In with Slack workflows"""

    def get(self):
        logger.info("Slack Signing OAuth Callback")
        user = process_slack_sign_in_callback(request.url)
        login_user(user)
        return redirect(url_for("web.settings_view"))
