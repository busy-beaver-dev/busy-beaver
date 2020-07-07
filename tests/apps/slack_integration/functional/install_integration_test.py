from datetime import time

import pytest
import responses

from busy_beaver.apps.slack_integration.oauth.oauth_flow import (
    SlackInstallationOAuthFlow,
)
from busy_beaver.models import GitHubSummaryConfiguration, SlackInstallation
from tests._utilities import FakeSlackClient


@pytest.fixture
def patch_slack(patcher):
    def _patch_slack(module_to_patch_slack, *, is_admin=None, details=None):
        obj = FakeSlackClient(is_admin=is_admin, details=details)
        patcher(module_to_patch_slack, namespace="SlackClient", replacement=obj)
        return obj

    return _patch_slack


@pytest.mark.end2end
@responses.activate
def test_slack_oauth_flow_first_time_installation(
    client, login_client, session, factory, patch_slack, create_slack_headers
):
    patched_slack = patch_slack("busy_beaver.apps.slack_integration.oauth.workflow")
    authorizing_user_id = "abc"
    workspace_id = "T9TK3CUKW"

    # Step 1 -- User installs app user Slack install link
    # Arrange
    bot_access_token = "xoxb-17653672481-19874698323-pdFZKVeTuE8sk7oOcBrzbqgy"
    responses.add(
        responses.POST,
        SlackInstallationOAuthFlow.TOKEN_URL,
        match_querystring=False,
        json={
            "ok": True,
            "access_token": bot_access_token,
            "token_type": "bot",
            "scope": "commands,incoming-webhook",
            "bot_user_id": "U0KRQLJ9H",
            "app_id": "A0KRD7HC3",
            "team": {"name": "Slack Softball Team", "id": workspace_id},
            "enterprise": {"name": "slack-sports", "id": "E12345678"},
            "authed_user": {
                "id": authorizing_user_id,
                "scope": "chat:write",
                "access_token": "xoxp-1234",
                "token_type": "user",
            },
        },
    )

    # Act -- oauth callback and token exchange
    params = {"code": "issued_code", "state": ""}
    response = client.get("/slack/installation-callback", query_string=params)

    # Assert -- confirm info in database is as expected
    assert response.status_code == 200
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-1234"
    assert installation.scope == "commands,incoming-webhook"
    assert installation.workspace_name == "Slack Softball Team"
    assert installation.workspace_id == workspace_id
    assert installation.authorizing_user_id == authorizing_user_id
    assert installation.bot_user_id == "U0KRQLJ9H"
    assert installation.bot_access_token == bot_access_token

    # ---
    # Step 2 -- Use invites bot to room
    # Arrange
    channel = "busy-beaver"
    data = {
        "type": "event_callback",
        "team_id": installation.workspace_id,
        "event": {
            "type": "member_joined_channel",
            "channel_type": "im",
            "user": installation.bot_user_id,
            "channel": channel,
        },
    }
    headers = create_slack_headers(100_000_000, data)

    # Act -- event_subscription callback
    client.post("/slack/event-subscription", headers=headers, json=data)

    # Assert -- confirm info in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.state == "config_requested"

    github_summary_config = GitHubSummaryConfiguration.query.first()
    assert github_summary_config.channel == channel

    # Assert -- check if config request set
    args, kwargs = patched_slack.mock.call_args
    assert "settings/github-summary|Configure when to post messages" in args[0]
    assert kwargs["user_id"] == authorizing_user_id

    # ---
    # Step 3 -- Update GitHub Summary configuration
    # Arrange
    slack_user = factory.SlackUser(installation=installation)
    logged_in_client = login_client(slack_user)
    patched_slack = patch_slack(
        "busy_beaver.apps.web.views", is_admin=True, details={"name": "busy_beaver"}
    )

    # Act
    data = {
        "summary_post_time": "14:00",
        "summary_post_timezone": "America/Chicago",
        "csrf_token": "token",
    }
    result = logged_in_client.post("/settings/github-summary", data=data)

    # Assert
    assert result.status_code

    installation = SlackInstallation.query.first()
    assert installation.state == "active"
    assert installation.github_summary_config.summary_post_time == time(14, 00)
    assert (
        installation.github_summary_config.summary_post_timezone.zone
        == "America/Chicago"
    )


@pytest.mark.end2end
@responses.activate
def test_slack_oauth_flow_reinstallation(client, session, factory, patch_slack):
    # Arrange
    patch_slack("busy_beaver.apps.slack_integration.oauth.workflow")

    # Create installation in database
    workspace_id = "T9TK3CUKW"
    workspace_name = "Slack Softball Team"
    installation = factory.SlackInstallation(
        workspace_id=workspace_id, workspace_name=workspace_name
    )
    factory.GitHubSummaryConfiguration(slack_installation=installation)

    # Create response to send back during token exchange
    bot_access_token = "xoxb-17653672481-19874698323-pdFZKVeTuE8sk7oOcBrzbqgy"
    responses.add(
        responses.POST,
        SlackInstallationOAuthFlow.TOKEN_URL,
        json={
            "ok": True,
            "access_token": bot_access_token,
            "token_type": "bot",
            "scope": "commands,incoming-webhook",
            "bot_user_id": "U0KRQLJ9H",
            "app_id": "A0KRD7HC3",
            "team": {"name": workspace_name, "id": workspace_id},
            "enterprise": {"name": "slack-sports", "id": "E12345678"},
            "authed_user": {
                "id": "U1234",
                "scope": "chat:write",
                "access_token": "xoxp-1234",
                "token_type": "user",
            },
        },
    )

    # Act -- oauth callback and token exchange
    params = {"code": "issued_code", "state": ""}
    response = client.get("/slack/installation-callback", query_string=params)

    # Assert -- information in database is as expected
    assert response.status_code == 200
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-1234"
    assert installation.scope == "commands,incoming-webhook"
    assert installation.workspace_name == workspace_name
    assert installation.workspace_id == workspace_id
    assert installation.authorizing_user_id == "U1234"
    assert installation.bot_user_id == "U0KRQLJ9H"
    assert installation.bot_access_token == bot_access_token
