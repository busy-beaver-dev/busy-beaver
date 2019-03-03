from flask import blueprints
from .github import GitHubIdentityVerificationCallbackResource
from .slack import SlackEventSubscriptionResource

integration_bp = blueprints.Blueprint("integrations", __name__)

integration_bp.add_url_rule(
    "/slack-event-subscription",
    view_func=SlackEventSubscriptionResource.as_view("slack_event_subscription"),
)
integration_bp.add_url_rule(
    "/github-integration",
    view_func=GitHubIdentityVerificationCallbackResource.as_view("github_verification"),
)
