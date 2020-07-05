import logging

from flask import jsonify, request
from flask.views import MethodView

from busy_beaver.apps.slack_integration.oauth.state_machine import (
    SlackInstallationOnboardUserWorkflow,
)
from busy_beaver.apps.slack_integration.oauth.workflow import (
    process_slack_installation_callback,
    process_slack_sign_in_callback,
)

logger = logging.getLogger(__name__)


class SlackAppInstallationCallbackResource(MethodView):
    """Callback endpoint for installing app into Slack workspace"""

    # TODO add redirect URI

    def get(self):
        logger.info("Slack Workspace Installation")
        # state is not used but it fits OAuth interface
        state = request.args.get("state")
        callback_url = request.url
        installation = process_slack_installation_callback(callback_url, state)
        onboard_user_workflow = SlackInstallationOnboardUserWorkflow(installation)
        onboard_user_workflow.advance()
        # TODO take them an actual page
        return jsonify({"Installation": "successful"})


class SlackSignInCallbackResource(MethodView):
    """Callback endpoint for Sign In with Slack workflows"""

    def get(self):
        logger.info("Slack Signing OAuth Callback")
        params = request.args
        state = params.get("state")
        callback_url = request.url

        user = process_slack_sign_in_callback(callback_url, state)

        if user.is_admin:
            return jsonify({"message": "You are the admin!"})
        else:
            return jsonify({"message": "You are not the admin!"})
