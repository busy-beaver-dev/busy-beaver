from flask import request
from busy_beaver.exceptions import UnverifiedSlackRequest

required_headers = ["X-Slack-Signature", "X-Slack-Request-Timestamp"]
REQUIRED_HEADERS = set(required_headers)


def slack_verification_required(func):
    def _wrapper():
        request_headers = set(header for header, value in request.headers)
        missing_headers = REQUIRED_HEADERS - request_headers != set()
        if missing_headers:
            raise UnverifiedSlackRequest("Invalid header")
        return func()

    return _wrapper
