from flask import Flask, jsonify, request
import pytest

from busy_beaver.app import handle_http_error
from busy_beaver.decorators import authentication_required
from busy_beaver.exceptions import NotAuthorized
from busy_beaver.models import ApiUser

TOKEN = "test_token_to_insert"
AUTH_HEADER = {"Authorization": f"token {TOKEN}"}


@pytest.fixture(scope="module")
def auth_app(app):
    @app.route("/test-no-auth")
    def no_auth():
        return jsonify({"hello": "world"})

    @app.route("/test-auth-required")
    @authentication_required(roles=["admin"])
    def auth_required():
        return jsonify({"hello": "world"})

    @app.route("/test-more-auth/<greeting>")
    @authentication_required(roles=["admin"])
    def more_auth(greeting):
        return jsonify({"key": f"{greeting}"})

    @app.route("/test-auth-required-user-role")
    @authentication_required(roles=["user"])
    def auth_required_user_role(greeting):
        return jsonify({"hello": "user"})

    @app.route("/test-auth-return_user-name")
    @authentication_required(roles=["admin"])
    def auth_return_username():
        return jsonify({"username": f"{request._internal['user'].username}"})

    app.register_error_handler(NotAuthorized, handle_http_error)
    yield app


@pytest.fixture(scope="module")
def client(auth_app):
    yield auth_app.test_client()


@pytest.fixture
def persist_api_user(session):
    user = ApiUser(username="test", token=TOKEN, role="admin")
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user


def test_no_auth_endpoint(client, persist_api_user):
    r = client.get("/test-no-auth")
    assert r.json == {"hello": "world"}


def test_auth_without_headers(client, persist_api_user):
    r = client.get("/test-auth-required")
    assert r.status_code == 401
    assert "Missing header: Authorization" in r.json["error"]["message"]


def test_auth_incorrect_token(client, persist_api_user):
    r = client.get("/test-auth-required", headers={"Authorization": "token not-there"})
    assert r.status_code == 401
    assert "Invalid token" in r.json["error"]["message"]


def test_auth_success(client, persist_api_user):
    r = client.get("/test-auth-required", headers=AUTH_HEADER)
    assert r.status_code == 200


def test_auth_with_url_variable(client, persist_api_user):
    RANDOM_STRING = "asdfbadsf"
    r = client.get(f"/test-more-auth/{RANDOM_STRING}", headers=AUTH_HEADER)
    assert r.status_code == 200
    assert RANDOM_STRING in r.json["key"]


def test_auth_adds_user_to_request_context(client, persist_api_user):
    r = client.get("/test-auth-return_user-name", headers=AUTH_HEADER)
    assert r.status_code == 200
    assert r.json["username"] == persist_api_user.username


@pytest.mark.parametrize("input", ["asdf", "jwt asdfasdfasdfasdf"])
def test_auth_header_with_incorrect_value(client, persist_api_user, input):
    r = client.get("/test-auth-required", headers={"Authorization": input})
    assert r.status_code == 401
    assert "Expected header" in r.json["error"]["message"]


def test_unauthorized_role(client, persist_api_user):
    r = client.get("/test-auth-required-user-role", headers=AUTH_HEADER)
    assert r.status_code == 401
    assert "Not authorized to access endpoint" in r.json["error"]["message"]


def test_raising_valueerror_by_passing_incorrect_roles_type():
    api = Flask(__name__)

    with pytest.raises(ValueError):

        @api.route("/auth")
        @authentication_required(roles="user")
        def auth():
            return jsonify({"hello": "world!"})
