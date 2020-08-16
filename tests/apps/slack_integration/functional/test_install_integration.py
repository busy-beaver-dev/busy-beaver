import pytest
import responses

from busy_beaver.apps.slack_integration.oauth.oauth_flow import (
    SlackInstallationOAuthFlow,
)
from busy_beaver.models import SlackInstallation
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

    # Assert -- message sent to user who installed
    post_message_args = patched_slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "`/busybeaver settings` to configure Busy Beaver" in args[0]
    assert kwargs["user_id"] == authorizing_user_id


@pytest.mark.end2end
@responses.activate
def test_slack_oauth_flow_reinstallation(client, session, factory, patch_slack):
    # Arrange
    patched_slack = patch_slack("busy_beaver.apps.slack_integration.oauth.workflow")

    # Create installation in database
    workspace_id = "T9TK3CUKW"
    workspace_name = "Slack Softball Team"
    authorizing_user_id = "abc"
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

    # Assert -- information in database is as expected
    assert response.status_code == 200
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-1234"
    assert installation.scope == "commands,incoming-webhook"
    assert installation.workspace_name == workspace_name
    assert installation.workspace_id == workspace_id
    assert installation.authorizing_user_id == authorizing_user_id
    assert installation.bot_user_id == "U0KRQLJ9H"
    assert installation.bot_access_token == bot_access_token

    # Assert -- message sent to user who installed
    post_message_args = patched_slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "`/busybeaver settings` to configure Busy Beaver" in args[0]
    assert kwargs["user_id"] == authorizing_user_id
