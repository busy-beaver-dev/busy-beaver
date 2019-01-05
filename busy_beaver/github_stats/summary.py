from datetime import datetime
from typing import List

from .event_list import (
    CommitsList,
    CreatedReposList,
    ForkedReposList,
    IssuesOpenedList,
    PublicizedReposList,
    PullRequestsList,
    ReleasesPublishedList,
    StarredReposList,
)
from ..adapters.github import GitHubAdapter
from ..config import oauth_token
from ..models import User

github = GitHubAdapter(oauth_token)


def generate_summary(user: User, boundary_dt: datetime):
    timeline = github.user_activity_after(user.github_username, boundary_dt)
    user_events = GitHubUserEvents(user, timeline)
    return user_events.generate_summary_text()


class GitHubUserEvents:
    def __init__(self, user: User, timeline: List[dict]):
        self.user = user
        self.events = {
            "releases_published": ReleasesPublishedList(),
            "created_repos": CreatedReposList(),
            "publicized_repos": PublicizedReposList(),
            "forked_repos": ForkedReposList(),
            "pull_requests": PullRequestsList(),
            "issues_opened": IssuesOpenedList(),
            "commits": CommitsList(),
            "starred_repos": StarredReposList(),
        }
        self._classify_events(timeline)
        pass

    def _classify_events(self, timeline):
        for event in timeline:
            payload = event["payload"]
            if (
                event["type"] == "CreateEvent"
                and payload.get("ref_type") == "repository"
            ):
                self.events["created_repos"].append(event)
            elif event["type"] == "ForkEvent":
                self.events["forked_repos"].append(event)
            elif event["type"] == "IssuesEvent" and payload.get("action") == "opened":
                self.events["issues_opened"].append(event)
            elif event["type"] == "PublicEvent":
                self.events["publicized_repos"].append(event)
            elif (
                event["type"] == "PullRequestEvent"
                and payload.get("action") == "opened"
            ):
                self.events["pull_requests"].append(event)
            elif event["type"] == "PushEvent":
                self.events["commits"].append(event)
            elif event["type"] == "ReleaseEvent":
                self.events["releases_published"].append(event)
            elif event["type"] == "WatchEvent" and payload.get("action") == "started":
                self.events["starred_repos"].append(event)

    def generate_summary_text(self):
        summary = ""
        for event_type, events in self.events.items():
            summary += events.generate_summary_text()

        if not summary:
            return ""

        user_info = "<@{slack_id}> as <https://github.com/{github_id}|{github_id}>\n"
        params = {
            "slack_id": self.user.slack_id,
            "github_id": self.user.github_username,
        }
        return user_info.format(**params) + summary + "\n"
