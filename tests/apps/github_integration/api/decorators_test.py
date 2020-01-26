import os

from flask import Flask, jsonify
import pytest

from busy_beaver.app import handle_http_error
from busy_beaver.apps.github_integration.api.decorators import verify_github_signature
from busy_beaver.exceptions import UnverifiedWebhookRequest

GITHUB_SIGNING_SECRET = "1824732430417652981161f3320885ed802cd374"
GITHUB_SIGNATURE = "sha1=6aa6592263da690736aec6d0e20a0d7c47b29bd3"


@pytest.fixture(scope="module")
def github_verification_app(app):
    @app.route("/github-only")
    @verify_github_signature(GITHUB_SIGNING_SECRET)
    def github_only():
        return jsonify({"authorization": "github_endpoint"})

    @app.route("/all-users")
    def unlocked_endpoint():
        return jsonify({"authorization": "all_users"})

    app.register_error_handler(UnverifiedWebhookRequest, handle_http_error)
    yield app


@pytest.fixture(scope="module")
def client(github_verification_app):
    yield github_verification_app.test_client()


def test_unlocked_endpoint_success(client):
    result = client.get("/all-users")
    assert result.status_code == 200


def test_github_verified_endpoint_failure_without_header(client):
    result = client.get("/github-only")
    assert result.status_code == 401


def test_github_verified_endpoint_failure_with_slack_signature_header(client):
    result = client.get("/github-only", headers={"X-Hub-Signature": GITHUB_SIGNATURE})
    assert result.status_code == 401


def test_github_verified_endpoint_failure_without_body(client):
    result = client.get("/github-only", headers={"X-Hub-Signature": GITHUB_SIGNATURE})
    assert result.status_code == 401


def test_github_verified_endpoint_success(client):
    # Arrange
    # TODO reading from file should be a fixture
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + "/json/github_response_bytes.txt", "rb") as f:
        data = f.read()
    headers = {"X-Hub-Signature": GITHUB_SIGNATURE}

    # Act
    result = client.get("/github-only", headers=headers, data=data)

    # Assert
    assert result.status_code == 200


@pytest.mark.parametrize("x", [None, 31, [234], (1,), set()])
def test_github_verification_decorator_raises_valueerror__signing_secret_env_not_set(x):
    api = Flask(__name__)

    with pytest.raises(ValueError):

        @api.route("/auth")
        @verify_github_signature(x)
        def auth():
            return jsonify({"hello": "world!"})
