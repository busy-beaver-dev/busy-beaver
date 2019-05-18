from flask import blueprints

from .github_summary import PublishGitHubSummaryResource
from .retweeter import TwitterPollingResource
from .youtube_post import YoutubePollingResource
from busy_beaver.decorators import authentication_required

tasks_bp = blueprints.Blueprint("tasks", __name__)
admin_role_required = authentication_required(roles=["admin"])

view = PublishGitHubSummaryResource.as_view("post_github_summary")
tasks_bp.add_url_rule(
    "/github-summary", view_func=admin_role_required(view), methods=["POST"]
)

view = TwitterPollingResource.as_view("twitter_poller")
tasks_bp.add_url_rule(
    "/poll-twitter", view_func=admin_role_required(view), methods=["POST"]
)

view = YoutubePollingResource.as_view("youtube_poller")
tasks_bp.add_url_rule(
    "/poll-youtube", view_func=admin_role_required(view), methods=["POST"]
)
