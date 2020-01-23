from flask import blueprints

from .event_subscription import GitHubEventSubscriptionResource
from .oauth import GitHubIdentityVerificationCallbackResource

github_bp = blueprints.Blueprint("github", __name__)

github_bp.add_url_rule(
    "/event-subscription",
    view_func=GitHubEventSubscriptionResource.as_view("github_event_subscription"),
)

github_bp.add_url_rule(
    "/oauth",
    view_func=GitHubIdentityVerificationCallbackResource.as_view("github_verification"),
)
