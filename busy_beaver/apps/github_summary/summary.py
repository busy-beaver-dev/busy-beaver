from datetime import datetime, timedelta

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

        username = user.github_username
        start_dt = boundary_dt
        end_dt = start_dt + timedelta(days=1)  # TODO depends on cadence

        timeline = github.user_activity_during_range(username, start_dt, end_dt)
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
