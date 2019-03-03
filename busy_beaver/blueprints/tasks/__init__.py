from flask import blueprints
from .github_summary import PublishGitHubSummaryResource
from .retweeter import TwitterPollingResource

integration_bp = blueprints.Blueprint("integrations", __name__)

integration_bp.add_url_rule(
    "/github-summary",
    view_func=PublishGitHubSummaryResource.as_view("post_github_summary"),
)
integration_bp.add_url_rule(
    "/poll-twitter",
    view_func=TwitterPollingResource.as_view("twitter_poller"),
)
