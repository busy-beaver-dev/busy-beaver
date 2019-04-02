from flask import blueprints

from .github import GitHubIdentityVerificationCallbackResource
from .slack import SlackEventSubscriptionResource
from busy_beaver.config import SLACK_SIGNING_SECRET
from busy_beaver.decorators import verify_slack_signature

integration_bp = blueprints.Blueprint("integrations", __name__)
slack_verification_required = verify_slack_signature(SLACK_SIGNING_SECRET)

view = SlackEventSubscriptionResource.as_view("slack_event_subscription")
integration_bp.add_url_rule("/slack-event-subscription", view_func=view)
integration_bp.add_url_rule(
    "/github-integration",
    view_func=GitHubIdentityVerificationCallbackResource.as_view("github_verification"),
)
