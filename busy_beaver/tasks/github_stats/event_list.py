import gettext

# Singular or Plural Form in Summary
commit_form = lambda n: gettext.ngettext("commit", "commits", n)  # noqa
issue_form = lambda n: gettext.ngettext("issue", "issues", n)  # noqa
pr_form = lambda n: gettext.ngettext("PR", "PRs", n)  # noqa
release_form = lambda n: gettext.ngettext("release", "releases", n)  # noqa
repo_form = lambda n: gettext.ngettext("repo", "repos", n)  # noqa


class EventList:
    def __init__(self):
        self.events = []

    def __repr__(self):
        return repr(self.events)

    def append(self, item):
        self.events.append(item)

    def generate_summary_text(self):
        if not self.events:
            return ""
        event_links = set([self._generate_link(event) for event in self.events])
        return self._format_text(event_links)

    @staticmethod
    def matches_event(event_params):
        return True

    def _format_text(self, links):
        return NotImplemented

    @staticmethod
    def _generate_link(event):
        repo_url = event["repo"]["url"]
        repo_url = repo_url.replace("api.github.com/repos/", "www.github.com/")
        repo_name = event["repo"]["name"]
        return f"<{repo_url}|{repo_name}>"


class CommitsList(EventList):
    @staticmethod
    def matches_event(event):
        return event.get("type") == "PushEvent"

    def _format_text(self, links):
        num = len(links)
        n_commits = sum([event["payload"]["distinct_size"] for event in self.events])
        return (
            f">:arrow_up: {n_commits} {commit_form(n_commits)} to "
            f"{num} {repo_form(num)}: {', '.join(links)}\n"
        )


class CreatedReposList(EventList):
    @staticmethod
    def matches_event(event):
        return (
            event.get("type") == "CreateEvent"
            and event.get("payload").get("ref_type") == "repository"
        )

    def _format_text(self, links):
        num = len(links)
        return f">:sparkles: {num} new {repo_form(num)}: {', '.join(links)}\n"


class ForkedReposList(EventList):
    @staticmethod
    def matches_event(event):
        return event.get("type") == "ForkEvent"

    def _format_text(self, links):
        emoji = ":fork_and_knife:"
        num = len(links)
        return f">{emoji} {num} forked {repo_form(num)}: {', '.join(links)}\n"


class IssuesOpenedList(EventList):
    @staticmethod
    def matches_event(event):
        return (
            event.get("type") == "IssuesEvent"
            and event.get("payload", {}).get("action") == "opened"
        )

    def _format_text(self, links):
        num = len(links)
        return f">:interrobang: {num} new {issue_form(num)}: {', '.join(links)}\n"

    @staticmethod
    def _generate_link(event):
        issue_url = event["payload"]["issue"]["html_url"]
        issue_number = event["payload"]["issue"]["number"]
        repo_name = event["repo"]["name"]
        return f"<{issue_url}|{repo_name}#{issue_number}>"


class PublicizedReposList(EventList):
    @staticmethod
    def matches_event(event):
        return event.get("type") == "PublicEvent"

    def _format_text(self, links):
        emoji = ":speaking_head_in_silhouette:"
        num = len(links)
        return f">{emoji} {num} {repo_form(num)} open-sourced: {', '.join(links)}\n"


class PullRequestsList(EventList):
    @staticmethod
    def matches_event(event):
        return (
            event.get("type") == "PullRequestEvent"
            and event.get("payload", {}).get("action") == "opened"
        )

    def _format_text(self, links):
        num = len(links)
        return f">:arrow_heading_up: {num} {pr_form(num)}: {', '.join(links)}\n"

    @staticmethod
    def _generate_link(event):
        pr_url = event["payload"]["pull_request"]["html_url"]
        pr_number = event["payload"]["pull_request"]["number"]
        repo_name = event["repo"]["name"]
        return f"<{pr_url}|{repo_name}#{pr_number}>"


class ReleasesPublishedList(EventList):
    @staticmethod
    def matches_event(event):
        return event.get("type") == "ReleaseEvent"

    def _format_text(self, links):
        num = len(links)
        return f">:ship: {num} new {release_form(num)}: {', '.join(links)}\n"


class StarredReposList(EventList):
    @staticmethod
    def matches_event(event):
        return (
            event.get("type") == "WatchEvent"
            and event.get("payload", {}).get("action") == "started"
        )

    def _format_text(self, links):
        num = len(links)
        return f">:star: {num} {repo_form(num)}: {', '.join(links)}\n"
