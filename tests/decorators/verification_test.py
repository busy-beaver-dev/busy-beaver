from flask import Flask, jsonify
import pytest

from busy_beaver.app import handle_http_error
from busy_beaver.decorators.verification import slack_verification_required
from busy_beaver.exceptions import UnverifiedSlackRequest

SLACK_SIGNING_SECRET = "8f742231b10e8888abcd99yyyzzz85a5"
SLACK_SIGNATURE = "v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503"


@pytest.fixture(scope="module")
def slack_verification_app(app):
    @app.route("/slack-only")
    @slack_verification_required(SLACK_SIGNING_SECRET)
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
            "X-Slack-Request-Timestamp": 1_531_420_618,
        },
    )
    assert result.status_code == 401


def test_slack_verified_endpoint_success(client):
    # TODO this will be constantly changing
    result = client.get(
        "/slack-only",
        headers={
            "X-Slack-Signature": SLACK_SIGNATURE,
            "X-Slack-Request-Timestamp": 1_531_420_618,
        },
        data=(
            "token=xyzz0WbapA4vBCDEFasx0q6G&team_id=T1DC2JH3J&team_domain=testteamnow&"
            "channel_id=G8PSS9T3V&channel_name=foobar&user_id=U2CERLKJA&"
            "user_name=roadrunner&command=%2Fwebhook-collect&text=&"
            "response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT1DC2JH3J%2F3977"
            "00885554%2F96rGlfmibIGlgcZRskXaIFfN&trigger_id=398738663015.47445629121.8"
            "03a0bc887a14d10d2c447fce8b6703c"
        ),
    )
    assert result.status_code == 200


@pytest.mark.parametrize("x", [None, 31, [234], (1,), set()])
def test_slack_verification_decorator_raises_valueerror__signing_secret_env_not_set(x):
    api = Flask(__name__)

    with pytest.raises(ValueError):

        @api.route("/auth")
        @slack_verification_required(None)
        def auth():
            return jsonify({"hello": "world!"})
