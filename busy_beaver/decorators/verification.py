from flask import request
from busy_beaver.exceptions import UnverifiedSlackRequest


def slack_verification_required(func):
    def _wrapper():
        if "X-Slack-Signature" not in request.headers:
            raise UnverifiedSlackRequest("Requires X-Slack-Signature header")
        return func()

    return _wrapper
