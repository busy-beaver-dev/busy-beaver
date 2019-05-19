from collections import OrderedDict
import json
from urllib.parse import urlencode

import pytest

from busy_beaver.config import SLACK_SIGNING_SECRET
from busy_beaver.decorators.verification import calculate_signature


@pytest.fixture
def create_slack_headers():
    """Dictionary get sorted when we retrieve the body, account for this"""

    def sort_dict(original_dict):
        res = OrderedDict()
        for k, v in sorted(original_dict.items()):
            if isinstance(v, dict):
                res[k] = dict(sort_dict(v))
            else:
                res[k] = v
        return dict(res)

    def wrapper(timestamp, data, is_json_data=True):
        if is_json_data:
            request_body = json.dumps(sort_dict(data)).encode("utf-8")
        else:
            request_body = urlencode(data).encode("utf-8")
        sig = calculate_signature(SLACK_SIGNING_SECRET, timestamp, request_body)
        return {"X-Slack-Request-Timestamp": timestamp, "X-Slack-Signature": sig}

    return wrapper
