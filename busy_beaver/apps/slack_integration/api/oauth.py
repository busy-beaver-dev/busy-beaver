import logging

from finite_state_machine.exceptions import InvalidStartState
from flask import jsonify, redirect, request, url_for
from flask.views import MethodView
from flask_login import login_user

from busy_beaver.apps.slack_integration.oauth.state_machine import (
    SlackInstallationOnboardUserStateMachine,
)
from busy_beaver.apps.slack_integration.oauth.workflow import (
    process_slack_installation_callback,
    process_slack_sign_in_callback,
)
from busy_beaver.extensions import db

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

        slack_installation_fsm = SlackInstallationOnboardUserStateMachine(installation)
        try:
            slack_installation_fsm.welcome_user()
        except InvalidStartState:
            pass
        else:
            installation.state = slack_installation_fsm.state
            db.session.add(installation)
            db.session.commit()

        try:
            slack_installation_fsm.save_new_slack_installation_information()
        except InvalidStartState:
            pass
        else:
            installation.state = slack_installation_fsm.state
            db.session.add(installation)
            db.session.commit()

        # TODO take them an actual page
        return jsonify({"Installation": "successful"})


class SlackSignInCallbackResource(MethodView):
    """Callback endpoint for Sign In with Slack workflows"""

    def get(self):
        logger.info("Slack Signing OAuth Callback")
        user = process_slack_sign_in_callback(request.url)
        login_user(user)
        return redirect(url_for("web.settings_view"))
