from dataclasses import dataclass, field
from datetime import timedelta
import gettext
from typing import List

from ..adapters.github import GitHubAdapter
from ..adapters.utilities import date_subtract
from ..config import oauth_token
from ..models import User

github = GitHubAdapter(oauth_token)
repo_text = lambda n: gettext.ngettext("repo", "repos", n)  # noqa
commit_text = lambda n: gettext.ngettext("commit", "commits", n)  # noqa


def generate_recent_activity_text(user: User):
    boundary_dt = date_subtract(timedelta(days=1))
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

    def generate_summary_text(self):
        # TODO implement rest
        text = ""
        text += self._create_repos_text()
        # text += self._forked_repos_text()
        # text += self._issues_opened_text()
        # text += self._publicized_repos_text()
        # text += self._pull_requests_text()
        text += self._commits_text()
        # text += self._releases_published_text()
        text += self._starred_repos_text()

        if not text:
            return ""

        text = (
            f"<@{self.user.slack_id}> as "
            f"<https://github.com/{self.user.github_username}|"
            f"{self.user.github_username}>\n"
        ) + text
        return text + "\n"

    def _create_repos_text(self):
        if not self.forked_repos:
            return ""

        repos = [generate_repo_link(event) for event in self.forked_repos]
        count = len(repos)
        return f">:sparkles: {count} new {repo_text(count)}: {', '.join(repos)}\n"

    def _forked_repos_text(self):
        return ""

    def _issues_opened_text(self):
        return ""

    def _publicized_repos_text(self):
        return ""

    def _pull_requests_text(self):
        return ""

    def _commits_text(self):
        if not self.commits:
            return ""

        repos = set([generate_repo_link(event) for event in self.commits])
        count = len(repos)
        num_commits = sum([event["payload"]["distinct_size"] for event in self.commits])
        return (
            f">:arrow_up: {num_commits} {commit_text(num_commits)} to "
            f"{count} {repo_text(count)}: {', '.join(repos)}\n"
        )

    def _releases_published_text(self):
        return ""

    def _starred_repos_text(self):
        if not self.starred_repos:
            return ""

        repos = [generate_repo_link(event) for event in self.starred_repos]
        count = len(repos)
        return f">:star: {count} {repo_text(count)}: {', '.join(repos)}\n"


def generate_repo_link(event):
    repo_url = event["repo"]["url"]
    repo_url = repo_url.replace(
        "https://api.github.com/repos/", "https://www.github.com/"
    )
    repo_name = event["repo"]["name"]
    return f"<{repo_url}|{repo_name}>"
