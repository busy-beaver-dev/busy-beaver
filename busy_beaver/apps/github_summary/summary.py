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
from busy_beaver.models import GitHubSummaryUser


class GitHubUserEvents:
    def __init__(self, user: GitHubSummaryUser, boundary_dt: datetime):
        self.user = user
        self.event_lists = [  # this is the order of summary output
            ReleasesPublishedList(),
            CreatedReposList(),
            PublicizedReposList(),
            ForkedReposList(),
            PullRequestsList(),
            IssuesOpenedList(),
            CommitsList(),
            StarredReposList(),
        ]

        timeline = github.user_activity_after(user.github_username, boundary_dt)
        for event in timeline:
            for event_list in self.event_lists:
                if event_list.matches_event(event):
                    event_list.append(event)

    def generate_summary_text(self):
        summary = ""
        for event_list in self.event_lists:
            summary += event_list.generate_summary_text()

        if not summary:
            return ""

        user_info = "<@{slack_id}> as <https://github.com/{github_id}|{github_id}>\n"
        params = {
            "slack_id": self.user.slack_id,
            "github_id": self.user.github_username,
        }
        return user_info.format(**params) + summary + "\n"
