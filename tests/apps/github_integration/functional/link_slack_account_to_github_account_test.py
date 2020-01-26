from urllib.parse import urlparse, parse_qs

import pytest
import responses

from busy_beaver.apps.github_integration.oauth.oauth_flow import GitHubOAuthFlow
from busy_beaver.common.wrappers.github import BASE_URL as GITHUB_BASE_URL

pytest_plugins = ("tests._utilities.fixtures.slack",)


@pytest.mark.end2end
@responses.activate
def test_link_slack_to_github__happy_path(
    client, factory, generate_slash_command_request, create_slack_headers
):
    # Arrange
    slack_id = "new_user"
    install = factory.SlackInstallation()

    # Create response to send back during token exchange
    responses.add(
        responses.POST,
        GitHubOAuthFlow.TOKEN_URL,
        json={"access_token": "access_token_1"},
    )
    # Create response for fetching GitHub user data
    responses.add(
        responses.GET,
        f"{GITHUB_BASE_URL}/user",
        json={"id": "github_id", "login": "github_username"},
    )

    # Step 1 -- User types `/busybeaver connect`
    data = generate_slash_command_request(
        "connect", user_id=slack_id, team_id=install.workspace_id
    )
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    # Server acknolwedges
    response = client.post("/slack/slash-command", headers=headers, data=data)
    assert response.status_code == 200

    # Grab state from response
    auth_url = response.get_json()["attachments"][0]["fallback"]
    parsed_auth_url = urlparse(auth_url)
    qs = parse_qs(parsed_auth_url.query)
    state = qs["state"][0]

    # Step 2 -- Click GitHub Link, confirm identity, success
    params = {"code": "issued_code", "state": state}
    response = client.get("/github/oauth", query_string=params)

    # Assert
    assert response.status_code == 200
    assert response.get_json() == {"Login": "successful"}


@pytest.mark.end2end
@responses.activate
def test_link_slack_to_github__invalid_state(
    client, factory, generate_slash_command_request, create_slack_headers
):
    # Arrange
    slack_id = "new_user"
    install = factory.SlackInstallation()

    # Create response to send back during token exchange
    responses.add(
        responses.POST,
        GitHubOAuthFlow.TOKEN_URL,
        json={"access_token": "access_token_1"},
    )
    # Create response for fetching GitHub user data
    responses.add(
        responses.GET,
        f"{GITHUB_BASE_URL}/user",
        json={"id": "github_id", "login": "github_username"},
    )

    # Step 1 -- User types `/busybeaver connect`
    data = generate_slash_command_request(
        "connect", user_id=slack_id, team_id=install.workspace_id
    )
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    # Server acknolwedges
    response = client.post("/slack/slash-command", headers=headers, data=data)
    assert response.status_code == 200

    # Grab state from response
    auth_url = response.get_json()["attachments"][0]["fallback"]
    parsed_auth_url = urlparse(auth_url)
    qs = parse_qs(parsed_auth_url.query)
    state = qs["state"][0]

    # Step 2 -- Somehow state gets modified, user clicks GitHub Link
    # confirms identify, and fails
    modified_state = state + state
    params = {"code": "issued_code", "state": modified_state}
    response = client.get("/github/oauth", query_string=params)

    # Assert
    assert response.status_code == 403
    assert response.get_json() == {
        "data": {},
        "error": {"message": "GitHub verification failed. Please try again."},
    }
