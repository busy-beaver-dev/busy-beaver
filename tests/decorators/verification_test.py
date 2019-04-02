from flask import jsonify
import pytest

from busy_beaver.app import handle_http_error
from busy_beaver.decorators.verification import slack_verification_required
from busy_beaver.exceptions import UnverifiedSlackRequest

SLACK_SIGNATURE = "v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503"


@pytest.fixture(scope="module")
def slack_verification_app(app):
    @app.route("/slack-only")
    @slack_verification_required
    def slack_only():
        return jsonify({"authorization": "slack_endpoint"})

    @app.route("/all-users")
    def unlocked_endpoint():
        return jsonify({"authorization": "all_users"})

    app.register_error_handler(UnverifiedSlackRequest, handle_http_error)
    yield app


@pytest.fixture(scope="module")
def client(slack_verification_app):
    yield slack_verification_app.test_client()


def test_unlocked_endpoint_success(client):
    result = client.get("/all-users")
    assert result.status_code == 200


def test_slack_verified_endpoint_failure_without_header(client):
    result = client.get("/slack-only")
    assert result.status_code == 401


def test_slack_verified_endpoint_failure_with_slack_signature_header(client):
    # TODO this will be constantly changing
    result = client.get("/slack-only", headers={"X-Slack-Signature": SLACK_SIGNATURE})
    assert result.status_code == 401


def test_slack_verified_endpoint_failure_without_body(client):
    result = client.get(
        "/slack-only",
        headers={
            "X-Slack-Signature": SLACK_SIGNATURE,
            "X-Slack-Request-Timestamp": "foo",
        },
    )
    assert result.status_code == 401


def test_slack_verified_endpoint_success(client):
    # TODO this will be constantly changing
    result = client.get(
        "/slack-only",
        headers={
            "X-Slack-Signature": SLACK_SIGNATURE,
            "X-Slack-Request-Timestamp": "foo",
        },
        data="command=/weather&text=94070",
    )
    assert result.status_code == 200
