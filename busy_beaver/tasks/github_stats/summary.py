from datetime import datetime

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
from busy_beaver import github
from busy_beaver.models import User


class GitHubUserEvents:
    def __init__(self, user: User, boundary_dt: datetime):
        self.user = user
        self.events = {  # this is the order of summary output
            "releases_published": ReleasesPublishedList(),
            "created_repos": CreatedReposList(),
            "publicized_repos": PublicizedReposList(),
            "forked_repos": ForkedReposList(),
            "pull_requests": PullRequestsList(),
            "issues_opened": IssuesOpenedList(),
            "commits": CommitsList(),
            "starred_repos": StarredReposList(),
        }

        timeline = github.user_activity_after(user.github_username, boundary_dt)
        self._classify_events(timeline)

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

    def _classify_events(self, timeline):
        for event in timeline:
            data = event["payload"]
            if event["type"] == "CreateEvent" and data.get("ref_type") == "repository":
                self.events["created_repos"].append(event)
            elif event["type"] == "ForkEvent":
                self.events["forked_repos"].append(event)
            elif event["type"] == "IssuesEvent" and data.get("action") == "opened":
                self.events["issues_opened"].append(event)
            elif event["type"] == "PublicEvent":
                self.events["publicized_repos"].append(event)
            elif event["type"] == "PullRequestEvent" and data.get("action") == "opened":
                self.events["pull_requests"].append(event)
            elif event["type"] == "PushEvent":
                self.events["commits"].append(event)
            elif event["type"] == "ReleaseEvent":
                self.events["releases_published"].append(event)
            elif event["type"] == "WatchEvent" and data.get("action") == "started":
                self.events["starred_repos"].append(event)
