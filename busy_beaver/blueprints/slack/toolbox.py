"""Slack toolbox"""


def make_slack_response(
    response_type="ephemeral", text="", attachments=None, blocks=None
):
    return {
        "response_type": response_type,
        "text": text,
        "attachments": [attachments] if attachments else [],
        "blocks": blocks if blocks else [],
    }
