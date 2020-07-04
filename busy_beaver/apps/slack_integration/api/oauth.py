import logging

from flask import jsonify, request
from flask.views import MethodView

from busy_beaver.apps.slack_integration.oauth.state_machine import (
    SlackInstallationOnboardUserWorkflow,
)
from busy_beaver.apps.slack_integration.oauth.workflow import (
    process_slack_installation_callback,
)

logger = logging.getLogger(__name__)


class SlackAppInstallationCallbackResource(MethodView):
    """Callback endpoint for installing app into Slack workspace"""

    def get(self):
        # state is not used but it fits OAuth interface
        state = request.args.get("state")
        callback_url = request.url
        installation = process_slack_installation_callback(callback_url, state)
        onboard_user_workflow = SlackInstallationOnboardUserWorkflow(installation)
        onboard_user_workflow.advance()
        return jsonify({"Installation": "successful"})
