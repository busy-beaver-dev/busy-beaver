import functools
import hashlib
import hmac

from flask import request

from busy_beaver.exceptions import UnverifiedWebhookRequest


def verify_github_signature(signing_secret: str):

    if not isinstance(signing_secret, str):
        raise ValueError

    def verification_decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            github_signature = request.headers.get("X-Hub-Signature", None)
            if not github_signature:
                raise UnverifiedWebhookRequest("Missing header")

            sig_parts = github_signature.split("=", maxsplit=1)
            if len(sig_parts) < 2 or sig_parts[0] != "sha1":
                raise UnverifiedWebhookRequest("Invalid signature")

            sig = calculate_signature(signing_secret, request.data)
            if signatures_unequal(sig, sig_parts[1]):
                raise UnverifiedWebhookRequest("Invalid")

            return func(*args, **kwargs)

        return _wrapper

    return verification_decorator


def calculate_signature(signing_secret, request_data):
    return hmac.new(str.encode(signing_secret), request_data, hashlib.sha1).hexdigest()


def signatures_unequal(request_hash, slack_signature):
    return not hmac.compare_digest(request_hash, slack_signature)
