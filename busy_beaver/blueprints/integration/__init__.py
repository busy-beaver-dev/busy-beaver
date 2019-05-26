from flask import blueprints
from .github import GitHubIdentityVerificationCallbackResource

integration_bp = blueprints.Blueprint("integrations", __name__)
integration_bp.add_url_rule(
    "/github-integration",
    view_func=GitHubIdentityVerificationCallbackResource.as_view("github_verification"),
)
