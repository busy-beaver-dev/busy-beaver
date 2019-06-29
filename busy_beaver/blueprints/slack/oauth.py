import logging

from flask import jsonify, request
from flask.views import MethodView

from busy_beaver.apps.external_integrations.workflow import (
    verify_callback_and_save_tokens_in_database,
)
from busy_beaver.sandbox.state_machine_spike import OnboardUserWorkflow

logger = logging.getLogger(__name__)


class SlackAppInstallationCallbackResource(MethodView):
    """Callback endpoint for installing app into Slack workspace"""

    def get(self):
        # state is not used but it fits OAuth interface
        state = request.args.get("state")
        callback_url = request.url
        installation = verify_callback_and_save_tokens_in_database(callback_url, state)
        onboard_user_workflow = OnboardUserWorkflow(installation)
        onboard_user_workflow.advance()
        return jsonify({"Installation": "successful"})
