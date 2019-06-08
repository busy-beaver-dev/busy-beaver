from busy_beaver import slack

github_discussion_channel = "busy-beaver-meta"


def post_new_issue_to_slack(data):
    action = data.get("action", None)
    if action != "opened":
        return

    html_url = data["issue"]["html_url"]
    message = f"*New Issue*: {html_url}"
    slack.post_message(message=message, channel=github_discussion_channel)


def post_new_pull_request_to_slack(data):
    action = data.get("action", None)
    if action != "opened":
        return

    html_url = data["pull_request"]["html_url"]
    message = f"*New Pull Request*: {html_url}"
    slack.post_message(message=message, channel=github_discussion_channel)
