import hashlib
import hmac
from flask import request
from busy_beaver.exceptions import UnverifiedSlackRequest

SLACK_SIGNING_SECRET = "8f742231b10e8888abcd99yyyzzz85a5"


def slack_verification_required(func):
    def _wrapper():
        timestamp = request.headers.get("X-Slack-Request-Timestamp", None)
        slack_signature = request.headers.get("X-Slack-Signature", None)
        if not timestamp or not slack_signature:
            raise UnverifiedSlackRequest("Invalid")

        req = str.encode("v0:" + str(timestamp) + ":") + request.get_data()
        hmac_val = hmac.new(str.encode(SLACK_SIGNING_SECRET), req, hashlib.sha256)
        request_hash = "v0=" + hmac_val.hexdigest()
        result = hmac.compare_digest(request_hash, slack_signature)

        if not result:
            raise UnverifiedSlackRequest("Invalid")

        return func()

    return _wrapper
