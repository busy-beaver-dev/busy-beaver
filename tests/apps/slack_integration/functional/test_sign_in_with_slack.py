from urllib.parse import parse_qs, urlparse

import pytest
import responses

from busy_beaver.apps.slack_integration.oauth.oauth_flow import SlackSignInOAuthFlow
from tests._utilities import FakeSlackClient

pytest_plugins = ("tests._utilities.fixtures.slack",)

MODULE_TO_TEST = "busy_beaver.apps.slack_integration.oauth.workflow"


@pytest.fixture
def patched_slack(patcher):
    def _wrapper(is_admin):
        obj = FakeSlackClient(is_admin=is_admin)
        return patcher(MODULE_TO_TEST, namespace="SlackClient", replacement=obj)

    return _wrapper


@pytest.mark.end2end
@responses.activate
@pytest.mark.parametrize(
    "is_admin, message",
    [(True, "You are the admin!"), (False, "You are not the admin!")],
)
def test_slack_sign_in__happy_path(
    is_admin,  # parameter
    message,  # parameter
    client,
    factory,
    generate_slash_command_request,
    create_slack_headers,
    patched_slack,
):
    # Step 1 -- User enters `/busybeaver settings`
    # Arrange
    slack_id = "new_user"
    install = factory.SlackInstallation()

    data = generate_slash_command_request(
        "settings", user_id=slack_id, team_id=install.workspace_id
    )
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    # Act
    response = client.post("/slack/slash-command", headers=headers, data=data)

    # Assert -- response is as expected
    assert response.status_code == 200
    auth_url = response.json["attachments"][0]["actions"][0]["url"]
    assert "user_scope=identity.basic" in auth_url
    assert "/oauth/v2/authorize" in auth_url
    assert "slack%2Fsign-in-callback" in auth_url

    # ---
    # Step 2 -- Confirm identity
    # Arrange
    # Grab state from response
    parsed_auth_url = urlparse(auth_url)
    qs = parse_qs(parsed_auth_url.query)
    state = qs["state"][0]

    # Create response to send back during token exchange
    responses.add(
        responses.GET,
        SlackSignInOAuthFlow.TOKEN_URL,
        match_querystring=False,
        json={
            "ok": True,
            "app_id": "A0118NQPZZC",
            "authed_user": {
                "id": slack_id,
                "scope": "identity.basic,identity.email,identity.avatar,identity.team",
                "access_token": "xoxp-yoda-yoda-yoda",
                "token_type": "user",
            },
            "team": {"id": install.workspace_id},
            "enterprise": "",
            "is_enterprise_install": False,
        },
    )

    # Stub out Slack client
    patched_slack(is_admin=is_admin)

    # Act
    params = {"code": "issued_code", "state": state}
    response = client.get("/slack/sign-in-callback", query_string=params)

    # Assert
    assert response.status_code == 302
    assert "/settings" in response.headers["Location"]


@pytest.mark.end2end
@responses.activate
def test_slack_sign_in__slack_token_exchange_fails__server_error(
    client, factory, generate_slash_command_request, create_slack_headers, patched_slack
):
    # Step 1 -- User enters `/busybeaver settings`
    # Arrange
    slack_id = "new_user"
    install = factory.SlackInstallation()

    data = generate_slash_command_request(
        "settings", user_id=slack_id, team_id=install.workspace_id
    )
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    # Act
    response = client.post("/slack/slash-command", headers=headers, data=data)

    # Assert -- response is as expected
    assert response.status_code == 200
    auth_url = response.json["attachments"][0]["actions"][0]["url"]
    assert "user_scope=identity.basic" in auth_url
    assert "/oauth/v2/authorize" in auth_url
    assert "slack%2Fsign-in-callback" in auth_url

    # ---
    # Step 2 -- Confirm identity
    # Arrange
    # Grab state from response
    parsed_auth_url = urlparse(auth_url)
    qs = parse_qs(parsed_auth_url.query)
    state = qs["state"][0]

    # Create error response to send back during token exchange
    responses.add(
        responses.GET,
        SlackSignInOAuthFlow.TOKEN_URL,
        match_querystring=False,
        status=400,
        json={},
    )

    # Stub out Slack client
    patched_slack(is_admin=True)

    # Act
    params = {"code": "issued_code", "state": state}
    response = client.get("/slack/sign-in-callback", query_string=params)

    # Assert
    assert response.status_code == 403
    assert "Server error." in response.get_json()["error"]["message"]


@pytest.mark.end2end
@responses.activate
def test_slack_sign_in__slack_token_exchange_fails__code_error(
    client, factory, generate_slash_command_request, create_slack_headers, patched_slack
):
    # Step 1 -- User enters `/busybeaver settings`
    # Arrange
    slack_id = "new_user"
    install = factory.SlackInstallation()

    data = generate_slash_command_request(
        "settings", user_id=slack_id, team_id=install.workspace_id
    )
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    # Act
    response = client.post("/slack/slash-command", headers=headers, data=data)

    # Assert -- response is as expected
    assert response.status_code == 200
    auth_url = response.json["attachments"][0]["actions"][0]["url"]
    assert "user_scope=identity.basic" in auth_url
    assert "/oauth/v2/authorize" in auth_url
    assert "slack%2Fsign-in-callback" in auth_url

    # ---
    # Step 2 -- Confirm identity
    # Arrange
    # Grab state from response
    parsed_auth_url = urlparse(auth_url)
    qs = parse_qs(parsed_auth_url.query)
    state = qs["state"][0]

    # Create error response to send back during token exchange
    responses.add(
        responses.GET,
        SlackSignInOAuthFlow.TOKEN_URL,
        match_querystring=False,
        status=200,
        json={"ok": False, "error": "Something went wrong"},
    )

    # Stub out Slack client
    patched_slack(is_admin=True)

    # Act
    params = {"code": "issued_code", "state": state}
    response = client.get("/slack/sign-in-callback", query_string=params)

    # Assert
    assert response.status_code == 403
    assert "Something went wrong" in response.get_json()["error"]["message"]
