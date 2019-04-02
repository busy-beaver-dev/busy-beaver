from flask import request
from busy_beaver.exceptions import UnverifiedSlackRequest

VERSION_STRING = "v0"


def slack_verification_required(func):
    def _wrapper():
        slack_request_ts = request.headers.get("X-Slack-Request-Timestamp", None)
        slack_signature = request.headers.get("X-Slack-Signature", None)
        request_body = request.get_data().decode("utf-8")
        if not slack_request_ts or not slack_signature or not request_body:
            raise UnverifiedSlackRequest("Invalid")

        # calcu = f"{VERSION_STRING}:{slack_request_ts}:{request_body}"

        # import pdb; pdb.set_trace()

        # Concatenate the version number, the timestamp, and the body of the request
        # to form a basestring. Use a colon as the delimiter between the three elements.
        # For example, v0:123456789:command=/weather&text=94070. The version number
        # right now is always v0.
        #
        # With the help of HMAC SHA256 implemented in your favorite programming, hash
        # the above basestring, using the Slack Signing Secret as the key.

        # Compare this computed signature to the X-Slack-Signature header on the
        # request.

        return func()

    return _wrapper
