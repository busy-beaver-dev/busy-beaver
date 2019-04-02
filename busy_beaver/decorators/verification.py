import functools
import hashlib
import hmac
from flask import request
from busy_beaver.exceptions import UnverifiedSlackRequest


def verify_slack_signature(signing_secret: str):

    if not isinstance(signing_secret, str):
        raise ValueError

    def verification_decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            timestamp = request.headers.get("X-Slack-Request-Timestamp", None)
            slack_signature = request.headers.get("X-Slack-Signature", None)
            if not timestamp or not slack_signature:
                raise UnverifiedSlackRequest("Invalid")

            sig = calculate_signature(signing_secret, timestamp, request.get_data())
            if signatures_unequal(sig, slack_signature):
                raise UnverifiedSlackRequest("Invalid")

            return func(*args, **kwargs)

        return _wrapper

    return verification_decorator


def calculate_signature(signing_secret, timestamp, request_body):
    req = str.encode("v0:" + str(timestamp) + ":") + request_body
    hmac_val = hmac.new(str.encode(signing_secret), req, hashlib.sha256)
    return "v0=" + hmac_val.hexdigest()


def signatures_unequal(request_hash, slack_signature):
    return not hmac.compare_digest(request_hash, slack_signature)
