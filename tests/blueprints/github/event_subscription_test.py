from collections import OrderedDict
import json
from urllib.parse import urlencode

import pytest

from busy_beaver.blueprints.github.decorators import calculate_signature
from busy_beaver.config import GITHUB_SIGNING_SECRET
from tests.utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.blueprints.github.event_subscription"
pytest_plugins = ("tests.fixtures.github",)


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


@pytest.mark.integration
def test_missing_event_type_header(
    client, create_github_headers, generate_event_subscription_request
):
    data = generate_event_subscription_request()
    headers = create_github_headers(data, event="ping", is_json_data=True)
    headers.pop("X-GitHub-Event")

    response = client.post("/github/event-subscription", headers=headers, json=data)

    assert response.status_code == 401


@pytest.mark.integration
def test_ping_event(client, create_github_headers, generate_event_subscription_request):
    data = generate_event_subscription_request()
    headers = create_github_headers(data, event="ping", is_json_data=True)

    response = client.post("/github/event-subscription", headers=headers, json=data)

    assert response.status_code == 200


# Thinking out loud...
# I really don't like writing these types of tests.
# They just confirm my API works, but don't really do anything
# Can we automate the end-to-end API test with a better test helper?
# just hit a bunch of endpoints and confirm it's a 200
@pytest.fixture
def patched_slack(patcher):
    obj = FakeSlackClient()
    return patcher(MODULE_TO_TEST, namespace="slack", replacement=obj)


@pytest.mark.integration
def test_new_issue_event(
    client, generate_event_subscription_request, patched_slack, create_github_headers
):
    # Arrange
    url = "https://github.com/busy-beaver-dev/busy-beaver/issues/155"
    data = generate_event_subscription_request(action="opened", issue_html_url=url)
    headers = create_github_headers(data, event="issues", is_json_data=True)

    response = client.post("/github/event-subscription", headers=headers, json=data)

    assert response.status_code == 200
    args, kwargs = patched_slack.mock.call_args
    assert "New Issue" in kwargs["message"]


@pytest.mark.integration
def test_pull_request_event(
    client, generate_event_subscription_request, patched_slack, create_github_headers
):
    # Arrange
    url = "https://github.com/busy-beaver-dev/busy-beaver/pull/138"
    data = generate_event_subscription_request(action="opened", pr_html_url=url)
    headers = create_github_headers(data, event="pull_request", is_json_data=True)

    response = client.post("/github/event-subscription", headers=headers, json=data)

    assert response.status_code == 200
    args, kwargs = patched_slack.mock.call_args
    assert "New Pull Request" in kwargs["message"]
