import functools
import hashlib
import hmac

from flask import request

from busy_beaver.config import SLACK_SIGNING_SECRET
from busy_beaver.exceptions import UnverifiedWebhookRequest


def verify_slack_signature(signing_secret: str):

    if not isinstance(signing_secret, str):
        raise ValueError

    def verification_decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            timestamp = request.headers.get("X-Slack-Request-Timestamp", None)
            slack_signature = request.headers.get("X-Slack-Signature", None)
            if not timestamp or not slack_signature:
                raise UnverifiedWebhookRequest("Invalid")

            sig = calculate_signature(signing_secret, timestamp, request.get_data())
            if signatures_unequal(sig, slack_signature):
                raise UnverifiedWebhookRequest("Invalid")

            return func(*args, **kwargs)

        return _wrapper

    return verification_decorator


slack_verification_required = verify_slack_signature(SLACK_SIGNING_SECRET)


def calculate_signature(signing_secret, timestamp, data):
    req = str.encode("v0:" + str(timestamp) + ":") + data
    return "v0=" + hmac.new(str.encode(signing_secret), req, hashlib.sha256).hexdigest()


def signatures_unequal(request_hash, slack_signature):
    return not hmac.compare_digest(request_hash, slack_signature)
