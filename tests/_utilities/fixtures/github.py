import pytest


@pytest.fixture
def generate_event_subscription_request():
    def _generate_data(
        *, action="", issue_html_url="", pr_html_url="", release_html_url=""
    ):
        request_json = {"action": action}
        if issue_html_url:
            request_json["issue"] = {"html_url": issue_html_url}
        if pr_html_url:
            request_json["pull_request"] = {"html_url": pr_html_url}
        if release_html_url:
            request_json["release"] = {"html_url": release_html_url}
        return request_json

    return _generate_data
