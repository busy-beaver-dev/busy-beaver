import logging

from flask import jsonify, request
from flask.views import MethodView

from .decorators import slack_verification_required
from busy_beaver.apps.slack_integration.slash_command import process_slash_command

logger = logging.getLogger(__name__)


class SlackSlashCommandDispatchResource(MethodView):
    """Dealing with slash commands"""

    decorators = [slack_verification_required]

    def post(self):
        data = dict(request.form)
        logger.info("Received Slack slash command", extra={"form_data": data})
        return jsonify(process_slash_command(data))
