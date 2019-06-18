from flask import blueprints

from .event_subscription import SlackEventSubscriptionResource
from .oauth import SlackWorkspaceInstallationResource
from .slash_command import SlackSlashCommandDispatchResource
from .verification import verify_slack_signature
from busy_beaver.config import SLACK_SIGNING_SECRET

slack_bp = blueprints.Blueprint("slack", __name__)
slack_verification_required = verify_slack_signature(SLACK_SIGNING_SECRET)

view = SlackEventSubscriptionResource.as_view("slack_event_subscription")
slack_bp.add_url_rule(
    "/event-subscription", view_func=slack_verification_required(view)
)

view = SlackSlashCommandDispatchResource.as_view("slack_slash_command_dispatcher")
slack_bp.add_url_rule("/slash-command", view_func=slack_verification_required(view))

view = SlackWorkspaceInstallationResource.as_view("slack_workspace_installation")
slack_bp.add_url_rule("/oauth", view_func=view)
