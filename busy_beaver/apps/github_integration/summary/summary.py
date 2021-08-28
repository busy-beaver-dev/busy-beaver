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
from busy_beaver.models import GitHubSummaryUser


class GitHubUserEvents:
    def __init__(self, user: GitHubSummaryUser, classified_events: list):
        self.user = user
        self.classified_events = classified_events

    @classmethod
    def classify_events_by_type(cls, user: GitHubSummaryUser, events: list):
        tracked_event_types = [  # this is the order of summary output
            ReleasesPublishedList(),
            CreatedReposList(),
            PublicizedReposList(),
            ForkedReposList(),
            PullRequestsList(),
            IssuesOpenedList(),
            CommitsList(),
            StarredReposList(),
        ]

        for event in events:
            for event_list in tracked_event_types:
                if event_list.matches_event(event):
                    event_list.append(event)

        return cls(user, tracked_event_types)

    def generate_summary_text(self):
        summary = ""
        for event_list in self.classified_events:
            summary += event_list.generate_summary_text()

        if not summary:
            return ""

        user_info = "<@{slack_id}> as <https://github.com/{github_id}|{github_id}>\n"
        params = {
            "slack_id": self.user.slack_id,
            "github_id": self.user.github_username,
        }
        return user_info.format(**params) + summary + "\n"
