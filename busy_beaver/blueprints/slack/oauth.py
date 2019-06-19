import logging

from flask import jsonify, redirect, request
from flask.views import MethodView

from busy_beaver.apps.external_integrations.workflow import (
    slack_generate_and_save_auth_tuple,
    slack_verify_callback_and_save_access_tokens_in_database,
)

logger = logging.getLogger(__name__)


class SlackWorkspaceInstallationCallbackResource(MethodView):
    """Callback endpoint for installing app into Slack workspace"""

    def get(self):
        state = request.args.get("state")
        callback_url = request.url
        slack_verify_callback_and_save_access_tokens_in_database(callback_url, state)
        return jsonify({"Login": "successful"})


class SlackWorkspaceInstallationRedirectResource(MethodView):
    def get(self):
        auth = slack_generate_and_save_auth_tuple()
        return redirect(auth.url, code=302)
