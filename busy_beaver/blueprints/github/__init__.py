from flask import blueprints

from .event_subscription import GitHubEventSubscriptionResource
from .oauth import GitHubIdentityVerificationCallbackResource
from .verification import verify_github_signature
from busy_beaver.config import GITHUB_SIGNING_SECRET

github_bp = blueprints.Blueprint("github", __name__)
github_verification_required = verify_github_signature(GITHUB_SIGNING_SECRET)

v = GitHubEventSubscriptionResource.as_view("github_event_subscription")
github_bp.add_url_rule("/event-subscription", view_func=github_verification_required(v))

v = GitHubIdentityVerificationCallbackResource.as_view("github_verification")
github_bp.add_url_rule("/oauth", view_func=v)
