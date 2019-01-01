from datetime import timedelta

from .adapters.github import GitHubAdapter
from .adapters.utilities import subtract_timedelta
from .config import oauth_token
from .models import User

github = GitHubAdapter(oauth_token)


def recent_activity_text(user: User):
    boundary_dt = subtract_timedelta(timedelta(days=1))
    activity = github.user_activity_after(user.github_username, boundary_dt)
    events_of_interest = find_events_of_interest(activity)
    return generate_recent_activity_text(user, events_of_interest)


def find_events_of_interest(activity):
    events_of_interest = []
    for event in activity:
        if event["type"] in ["PushEvent", "WatchEvent"]:
            event_of_interest = {}
            event_of_interest["type"] = event["type"]
            repo_url = event['repo']['url']
            repo_url = repo_url.replace(
                "https://api.github.com/repos/",
                "https://www.github.com/"
            )
            repo_name = event['repo']['name']
            event_of_interest["repo"] = f"<{repo_url}|{repo_name}>"

            if event["type"] == "PushEvent":
                event_of_interest["commit_count"] = len(event["payload"]["commits"])

            events_of_interest.append(event_of_interest)
    return events_of_interest


def generate_recent_activity_text(user, events_of_interest):
    if not events_of_interest:
        return ""

    text = (
        f"<@{user.slack_id}> as <https://github.com/{user.github_username}|"
        f"{user.github_username}>\n"
    )
    for event_type in sorted(list(set([e["type"] for e in events_of_interest]))):
        events = [
            event for event in events_of_interest if event["type"] == event_type
        ]
        repos = list(set([event["repo"] for event in events]))
        repo_count = len(repos)

        if repo_count > 1:
            repo_s = "s"
        else:
            repo_s = ""

        if event_type == "PushEvent":
            commit_count = sum([event["commit_count"] for event in events])
            if commit_count > 1:
                commit_s = "s"
            else:
                commit_s = ""
            text += (
                f">:arrow_up: {commit_count} commit{commit_s} to "
                f"{repo_count} repo{repo_s}: {', '.join(repos)}\n"
            )
        if event_type == "WatchEvent":
            text += f">:star: {repo_count} repo{repo_s}: {', '.join(repos)}\n"
    text += "\n"
    return text
