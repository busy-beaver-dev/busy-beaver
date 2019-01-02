from dataclasses import dataclass, field
import gettext
from typing import List

from ..models import User

repo_text = lambda n: gettext.ngettext("repo", "repos", n)  # noqa
commit_text = lambda n: gettext.ngettext("commit", "commits", n)  # noqa


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
        summary = ""
        summary += self._create_repos_text()
        # text += self._forked_repos_text()
        # text += self._issues_opened_text()
        # text += self._publicized_repos_text()
        # text += self._pull_requests_text()
        summary += self._commits_text()
        # text += self._releases_published_text()
        summary += self._starred_repos_text()

        if not summary:
            return ""

        user_info = "<@{slack_id}> as <https://github.com/{github_id}|{github_id}>\n"
        params = {
            "slack_id": self.user.slack_id,
            "github_id": self.user.github_username,
        }
        return user_info.format(**params) + summary + "\n"

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
