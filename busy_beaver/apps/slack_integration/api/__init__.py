from flask import blueprints

from .event_subscription import SlackEventSubscriptionResource
from .oauth import SlackAppInstallationCallbackResource, SlackSignInCallbackResource
from .slash_command import SlackSlashCommandDispatchResource

slack_bp = blueprints.Blueprint("slack", __name__)

slack_bp.add_url_rule(
    "/event-subscription",
    view_func=SlackEventSubscriptionResource.as_view("slack_event_subscription"),
)

slack_bp.add_url_rule(
    "/slash-command",
    view_func=SlackSlashCommandDispatchResource.as_view("slash_command_dispatcher"),
)

slack_bp.add_url_rule(
    "/installation-callback",
    view_func=SlackAppInstallationCallbackResource.as_view("slack_install_callback"),
)

slack_bp.add_url_rule(
    "/sign-in-callback",
    view_func=SlackSignInCallbackResource.as_view("slack_signin_callback"),
)
