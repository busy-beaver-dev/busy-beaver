import pytest
import responder

from busy_beaver import db
from busy_beaver.backend.decorators import authentication_required
from busy_beaver.models import ApiUser

TOKEN = "test_token_to_insert"
AUTH_HEADER = {"Authorization": f"token {TOKEN}"}


@pytest.fixture(scope="module")
def api():
    api = responder.API()

    @api.route("/no-auth")
    def no_auth(req, resp):
        resp.text = "hello, world!"

    @api.route("/auth-required")
    @authentication_required
    def auth_required(req, resp, user):
        resp.text = "hello, world!"

    @api.route("/more-auth/{greeting}")
    @authentication_required
    def more_auth(req, resp, user, *, greeting):
        resp.text = f"echo greeting: {greeting}"

    return api


@pytest.fixture
def persist_api_user():
    savepoint = db.session.begin_nested()
    db.session.begin_nested()

    user = ApiUser(username="test", token=TOKEN)
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)

    yield user

    savepoint.rollback()


def test_no_auth_endpoint(api):
    r = api.requests.get("/no-auth")
    assert r.text == "hello, world!"


def test_auth_without_headers(api):
    r = api.requests.get("/auth-required")
    assert r.status_code == 401
    assert "Missing header: Authorization" in r.text


def test_auth_incorrect_token(api):
    r = api.requests.get("/auth-required", headers={"Authorization": "token not-there"})
    assert r.status_code == 401
    assert "Invalid token" in r.text


def test_auth_success(api, persist_api_user):
    r = api.requests.get("/auth-required", headers=AUTH_HEADER)
    assert r.status_code == 200


def test_auth_with_url_variable(api, persist_api_user):
    RANDOM_STRING = "asdfbadsf"
    r = api.requests.get(f"/more-auth/{RANDOM_STRING}", headers=AUTH_HEADER)
    assert RANDOM_STRING in r.text


@pytest.mark.parametrize("input", ["asdf", "jwt asdfasdfasdfasdf"])
def test_auth_header_with_incorrect_value(input, api, persist_api_user):
    r = api.requests.get("/auth-required", headers={"Authorization": input})
    assert r.status_code == 401
    assert "Authorization specification" in r.text
