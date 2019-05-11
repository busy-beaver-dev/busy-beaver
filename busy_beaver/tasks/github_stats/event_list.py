import inflect

inflector = inflect.engine()


class EventList:
    EMOJI = ":heart:"
    NOUN = "event"

    def __init__(self):
        self.events = []

    def __repr__(self):
        return repr(self.events)  # pragma: no cover

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
        num = len(links)
        noun = inflector.plural(self.NOUN, num)
        link_output = ", ".join(links)
        return f">{self.EMOJI} {num} {noun} {link_output}\n"

    @staticmethod
    def _generate_link(event):
        repo_url = event["repo"]["url"]
        repo_url = repo_url.replace("api.github.com/repos/", "www.github.com/")
        repo_name = event["repo"]["name"]
        return f"<{repo_url}|{repo_name}>"


class CommitsList(EventList):
    EMOJI = ":arrow_up:"

    @staticmethod
    def matches_event(event):
        return event.get("type") == "PushEvent"

    def _format_text(self, links):
        num_repos = len(links)
        repo_noun = inflector.plural(self.NOUN, num_repos)

        num_commits = sum([event["payload"]["distinct_size"] for event in self.events])
        commit_noun = inflector.plural("commit", num_commits)
        return (
            f">{self.EMOJI} {num_commits} {commit_noun} "
            f"{num_repos} {repo_noun}: {', '.join(links)}\n"
        )


class CreatedReposList(EventList):
    EMOJI = ":sparkles:"
    NOUN = "new issue"

    @staticmethod
    def matches_event(event):
        return (
            event.get("type") == "CreateEvent"
            and event.get("payload").get("ref_type") == "repository"
        )


class ForkedReposList(EventList):
    EMOJI = ":fork_and_knife:"
    NOUN = "forked repo"

    @staticmethod
    def matches_event(event):
        return event.get("type") == "ForkEvent"


class IssuesOpenedList(EventList):
    EMOJI = ":interrobang:"
    NOUN = "new issue"

    @staticmethod
    def matches_event(event):
        return (
            event.get("type") == "IssuesEvent"
            and event.get("payload", {}).get("action") == "opened"
        )

    @staticmethod
    def _generate_link(event):
        issue_url = event["payload"]["issue"]["html_url"]
        issue_number = event["payload"]["issue"]["number"]
        repo_name = event["repo"]["name"]
        return f"<{issue_url}|{repo_name}#{issue_number}>"


class PublicizedReposList(EventList):
    EMOJI = ":speaking_head_in_silhouette:"
    NOUN = "open-sourced repo"

    @staticmethod
    def matches_event(event):
        return event.get("type") == "PublicEvent"


class PullRequestsList(EventList):
    EMOJI = ":arrow_heading_up:"
    NOUN = "PR"

    @staticmethod
    def matches_event(event):
        return (
            event.get("type") == "PullRequestEvent"
            and event.get("payload", {}).get("action") == "opened"
        )

    @staticmethod
    def _generate_link(event):
        pr_url = event["payload"]["pull_request"]["html_url"]
        pr_number = event["payload"]["pull_request"]["number"]
        repo_name = event["repo"]["name"]
        return f"<{pr_url}|{repo_name}#{pr_number}>"


class ReleasesPublishedList(EventList):
    EMOJI = ":ship:"
    NOUN = "new release"

    @staticmethod
    def matches_event(event):
        return event.get("type") == "ReleaseEvent"


class StarredReposList(EventList):
    EMOJI = ":star:"
    NOUN = "repo"

    @staticmethod
    def matches_event(event):
        return (
            event.get("type") == "WatchEvent"
            and event.get("payload", {}).get("action") == "started"
        )
