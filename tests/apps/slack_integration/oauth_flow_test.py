import pytest
import responses

from busy_beaver.apps.slack_integration.oauth.oauth_flow import (
    SlackInstallationOAuthFlow,
)
from busy_beaver.apps.slack_integration.oauth.workflow import (
    verify_callback_and_save_tokens_in_database,
)
from busy_beaver.models import SlackInstallation


@pytest.mark.unit
@responses.activate
def test_slack_oauth_flow_first_time_installation(session):
    # Arrange
    # Step 1 -- User goes to 3rd party website and authenticates app
    # Step 2 -- Create response to send back during token exchange
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
            "team": {"name": "Slack Softball Team", "id": "T9TK3CUKW"},
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
    state = ""
    code = "1234"
    qs = f"state={state}&code={code}"
    callback_url = f"https://app.busybeaverbot.com/slack/oauth?{qs}"
    verify_callback_and_save_tokens_in_database(callback_url, state)

    # Assert -- confirm info in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-1234"
    assert installation.scope == "commands,incoming-webhook"
    assert installation.workspace_name == "Slack Softball Team"
    assert installation.workspace_id == "T9TK3CUKW"
    assert installation.authorizing_user_id == "U1234"
    assert installation.bot_user_id == "U0KRQLJ9H"
    assert installation.bot_access_token == bot_access_token


@pytest.mark.unit
@responses.activate
def test_slack_oauth_flow_reinstallation(session, factory):
    # Arrange
    # Create installation in database
    workspace_id = "T9TK3CUKW"
    workspace_name = "Slack Softball Team"
    installation = factory.SlackInstallation(
        workspace_id=workspace_id, workspace_name=workspace_name
    )

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
    state = ""
    code = "1234"
    qs = f"state={state}&code={code}"
    callback_url = f"https://app.busybeaverbot.com/slack/oauth?{qs}"
    verify_callback_and_save_tokens_in_database(callback_url, state)

    # Assert -- information in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-1234"
    assert installation.scope == "commands,incoming-webhook"
    assert installation.workspace_name == workspace_name
    assert installation.workspace_id == workspace_id
    assert installation.authorizing_user_id == "U1234"
    assert installation.bot_user_id == "U0KRQLJ9H"
    assert installation.bot_access_token == bot_access_token
