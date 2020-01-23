def generate_new_issue_message(data):
    action = data.get("action", None)
    if action != "opened":
        return

    html_url = data["issue"]["html_url"]
    return f"*New Issue*: {html_url}"


def generate_new_pull_request_message(data):
    action = data.get("action", None)
    if action != "opened":
        return

    html_url = data["pull_request"]["html_url"]
    return f"*New Pull Request*: {html_url}"


def generate_new_release_message(data):
    action = data.get("action", None)
    if action != "published":
        return

    html_url = data["release"]["html_url"]
    return f"*New Release*: {html_url}"
