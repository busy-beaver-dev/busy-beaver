from flask import jsonify
import pytest

from busy_beaver.app import handle_http_error
from busy_beaver.decorators.verification import slack_verification_required
from busy_beaver.exceptions import UnverifiedSlackRequest


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


def test_slack_verified_endpoint_success(client):
    # TODO this will be constantly changing
    result = client.get("/slack-only", headers={"X-Slack-Signature": "foo"})
    assert result.status_code == 200
