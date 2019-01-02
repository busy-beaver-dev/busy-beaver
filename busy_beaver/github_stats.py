from dataclasses import dataclass, field
from datetime import timedelta
from typing import List

from .adapters.github import GitHubAdapter
from .adapters.utilities import subtract_date
from .config import oauth_token
from .models import User

github = GitHubAdapter(oauth_token)


def generate_recent_activity_text(user: User):
    boundary_dt = subtract_date(timedelta(days=1))
    user_timeline = github.user_activity_after(user.github_username, boundary_dt)
    user_events = classify_events(user, user_timeline)
    return user_events.generate_summary_text()


def classify_events(user: User, timeline: List[dict]):
    user_events = GitHubUserEvents(user=user)
    for event in timeline:
        etype = event["type"]
        if etype == "CreateEvent" and event["payload"].get("ref_type") == "repository":
            user_events.created_repos.append(event)
        elif etype == "ForkEvent":
            user_events.forked_repos.append(event)
        elif etype == "IssueEvents" and event["payload"].get("action") == "opened":
            user_events.issues_opened.append(event)
        elif event["type"] == "PublicEvent":
            user_events.publicized_repos.append(event)
        elif etype == "PullRequestEvent" and event["payload"].get("action") == "opened":
            user_events.pull_requests.append(event)
        elif etype == "PushEvent":
            user_events.commits.append(event)
        elif etype == "ReleaseEvent":
            user_events.releases_published.append(event)
        elif etype == "WatchEvent" and event["payload"].get("action") == "started":
            user_events.starred_repos.append(event)
    return user_events


@dataclass
class GitHubUserEvents:
    user: User
    created_repos: List[dict] = field(default_factory=list)
    forked_repos: List[dict] = field(default_factory=list)
    issues_opened: List[dict] = field(default_factory=list)
    publicized_repos: List[dict] = field(default_factory=list)
    pull_requests: List[dict] = field(default_factory=list)
    commits: List[dict] = field(default_factory=list)
    releases_published: List[dict] = field(default_factory=list)
    starred_repos: List[dict] = field(default_factory=list)

    def _create_repos_text(self):
        repos = [generate_link(event) for event in self.forked_repos]
        repo_count = len(repos)
        if repo_count == 0:
            return ""
        elif repo_count > 1:
            repo_s = "s"
        else:
            repo_s = ""
        return f">:sparkles: {repo_count} new repo{repo_s}: {', '.join(repos)}\n"

    def _forked_repos_text(self):
        return ""

    def _issues_opened_text(self):
        return ""

    def _publicized_repos_text(self):
        return ""

    def _pull_requests_text(self):
        return ""

    def _commits_text(self):
        repos = set([generate_link(event) for event in self.commits])
        repo_count = len(repos)
        if repo_count == 0:
            return ""
        elif repo_count > 1:
            repo_s = "s"
        else:
            repo_s = ""

        num_commits = sum([event["payload"]["distinct_size"] for event in self.commits])
        if num_commits > 1:
            commit_s = "s"
        else:
            commit_s = ""
        return (
            f">:arrow_up: {num_commits} commit{commit_s} to "
            f"{repo_count} repo{repo_s}: {', '.join(repos)}\n"
        )

    def _releases_published_text(self):
        return ""

    def _starred_repos_text(self):
        repos = [generate_link(event) for event in self.starred_repos]
        repo_count = len(repos)
        if repo_count == 0:
            return ""
        elif repo_count > 1:
            repo_s = "s"
        else:
            repo_s = ""
        return f">:star: {repo_count} repo{repo_s}: {', '.join(repos)}\n"

    def generate_summary_text(self):
        text = ""
        text += self._create_repos_text()
        text += self._forked_repos_text()
        text += self._issues_opened_text()
        text += self._publicized_repos_text()
        text += self._pull_requests_text()
        text += self._commits_text()
        text += self._releases_published_text()
        text += self._starred_repos_text()

        if text == "":
            return ""

        text = (
            f"<@{self.user.slack_id}> as "
            f"<https://github.com/{self.user.github_username}|"
            f"{self.user.github_username}>\n"
        ) + text
        return text + "\n"


def generate_link(event):
    repo_url = event["repo"]["url"]
    repo_url = repo_url.replace(
        "https://api.github.com/repos/", "https://www.github.com/"
    )
    repo_name = event["repo"]["name"]
    return f"<{repo_url}|{repo_name}>"
