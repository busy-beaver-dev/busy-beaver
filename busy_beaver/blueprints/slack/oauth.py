import logging

from flask import jsonify, request
from flask.views import MethodView

from busy_beaver.apps.external_integrations.workflow import (
    slack_verify_callback_and_save_access_tokens_in_database,
)

logger = logging.getLogger(__name__)


class SlackAppInstallationCallbackResource(MethodView):
    """Callback endpoint for installing app into Slack workspace"""

    def get(self):
        # state is not used but it fits OAuth interface
        state = request.args.get("state")
        callback_url = request.url
        slack_verify_callback_and_save_access_tokens_in_database(callback_url, state)
        return jsonify({"Installation": "successful"})
