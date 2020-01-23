from flask import blueprints

from .github_summary import PublishGitHubSummaryResource
from .retweeter import TwitterPollingResource
from .upcoming_events import PublishUpcomingEventsResource
from .update_events import AddEventPollingResource
from .youtube_post import YouTubePollingResource

poller_bp = blueprints.Blueprint("poller", __name__)

poller_bp.add_url_rule(
    "/github-summary",
    view_func=PublishGitHubSummaryResource.as_view("post_github_summary"),
    methods=["POST"],
)

poller_bp.add_url_rule(
    "/twitter",
    view_func=TwitterPollingResource.as_view("twitter_poller"),
    methods=["POST"],
)

poller_bp.add_url_rule(
    "/upcoming-events",
    view_func=PublishUpcomingEventsResource.as_view("post_upcoming_events"),
    methods=["POST"],
)

poller_bp.add_url_rule(
    "/sync-event-database",
    view_func=AddEventPollingResource.as_view("meetup_poller"),
    methods=["POST"],
)

poller_bp.add_url_rule(
    "/youtube",
    view_func=YouTubePollingResource.as_view("youtube_poller"),
    methods=["POST"],
)
