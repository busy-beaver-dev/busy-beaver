from collections import OrderedDict
import json
from urllib.parse import urlencode

import pytest

from busy_beaver.blueprints.github.verification import calculate_signature
from busy_beaver.config import GITHUB_SIGNING_SECRET


@pytest.fixture
def create_github_headers():
    """Dictionary get sorted when we retrieve the body, account for this"""

    def sort_dict(original_dict):
        res = OrderedDict()
        for k, v in sorted(original_dict.items()):
            if isinstance(v, dict):
                res[k] = dict(sort_dict(v))
            else:
                res[k] = v
        return dict(res)

    def wrapper(data, event="ping", is_json_data=True):
        if is_json_data:
            request_body = json.dumps(sort_dict(data)).encode("utf-8")
        else:
            request_body = urlencode(data).encode("utf-8")
        sig = calculate_signature(GITHUB_SIGNING_SECRET, request_body)
        return {"X-Hub-Signature": sig, "X-GitHub-Event": event}

    return wrapper


@pytest.fixture
def generate_event_subscription_request():
    def _generate_data():
        return {}

    return _generate_data


def test_ping_event_subscription(
    client, create_github_headers, generate_event_subscription_request
):
    data = generate_event_subscription_request()
    headers = create_github_headers(data, event="ping", is_json_data=True)

    response = client.post("/github/event-subscription", headers=headers, json=data)

    assert response.status_code == 200
