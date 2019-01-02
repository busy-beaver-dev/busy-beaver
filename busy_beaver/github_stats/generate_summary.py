from datetime import timedelta
from typing import List

from .user_events import GitHubUserEvents
from ..adapters.github import GitHubAdapter
from ..adapters.utilities import date_subtract
from ..config import oauth_token
from ..models import User

github = GitHubAdapter(oauth_token)


def generate_recent_activity_text(user: User):
    boundary_dt = date_subtract(timedelta(days=1))
    user_timeline = github.user_activity_after(user.github_username, boundary_dt)
    user_events = _classify_events(user, user_timeline)
    return user_events.generate_summary_text()


def _classify_events(user: User, timeline: List[dict]):
    user_events = GitHubUserEvents(user=user)
    for event in timeline:
        payload = event["payload"]
        if event["type"] == "CreateEvent" and payload.get("ref_type") == "repository":
            user_events.created_repos.append(event)
        elif event["type"] == "ForkEvent":
            user_events.forked_repos.append(event)
        elif event["type"] == "IssueEvents" and payload.get("action") == "opened":
            user_events.issues_opened.append(event)
        elif event["type"] == "PublicEvent":
            user_events.publicized_repos.append(event)
        elif event["type"] == "PullRequestEvent" and payload.get("action") == "opened":
            user_events.pull_requests.append(event)
        elif event["type"] == "PushEvent":
            user_events.commits.append(event)
        elif event["type"] == "ReleaseEvent":
            user_events.releases_published.append(event)
        elif event["type"] == "WatchEvent" and payload.get("action") == "started":
            user_events.starred_repos.append(event)
    return user_events
