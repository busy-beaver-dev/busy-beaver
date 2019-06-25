import pytest
import responses

from busy_beaver.apps.external_integrations.oauth_providers.slack import SlackOAuthFlow
from busy_beaver.apps.external_integrations.workflow import (
    slack_verify_callback_and_save_access_tokens_in_database,
)
from busy_beaver.models import SlackInstallation


@pytest.mark.integration
@responses.activate
def test_slack_oauth_flow_first_time_installation(session):
    # Arrange
    # Step 1 -- User goes to 3rd party website and authenticates app
    # Step 2 -- Create response to send back during token exchange
    responses.add(
        responses.POST,
        SlackOAuthFlow.TOKEN_URL,
        json={
            "access_token": "xoxp-XXXXXXXX-XXXXXXXX-XXXXX",
            "scope": "incoming-webhook,commands,bot",
            "team_name": "Team Installing Your Hook",
            "team_id": "TXXXXXXXXX",
            "user_id": "test_user",
            "bot": {
                "bot_user_id": "UTTTTTTTTTTR",
                "bot_access_token": "xoxb-XXXXXXXXXXXX-TTTTTTTTTTTTTT",
            },
        },
    )

    # Act -- oauth callback and token exchange
    state = ""
    code = "1234"
    qs = f"state={state}&code={code}"
    callback_url = f"https://busybeaver.sivji.com/slack/oauth?{qs}"
    slack_verify_callback_and_save_access_tokens_in_database(callback_url, state)

    # Assert -- confirm info in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-XXXXXXXX-XXXXXXXX-XXXXX"
    assert installation.scope == "incoming-webhook,commands,bot"
    assert installation.workspace_name == "Team Installing Your Hook"
    assert installation.workspace_id == "TXXXXXXXXX"
    assert installation.authorizing_user_id == "test_user"
    assert installation.bot_user_id == "UTTTTTTTTTTR"
    assert installation.bot_access_token == "xoxb-XXXXXXXXXXXX-TTTTTTTTTTTTTT"


@pytest.mark.end2end
@responses.activate
def test_slack_oauth_flow_reinstallation(fm):
    # Arrange
    # Create installation in database
    workspace_id = "TXXXXXXXXX"
    installation = fm.SlackInstallationFactory(
        workspace_id=workspace_id, workspace_name="Test"
    )

    # Create response to send back during token exchange
    responses.add(
        responses.POST,
        SlackOAuthFlow.TOKEN_URL,
        json={
            "access_token": "xoxp-XXXXXXXX-XXXXXXXX-XXXXX",
            "scope": "incoming-webhook,commands,bot",
            "team_name": "Team Installing Your Hook",
            "team_id": workspace_id,
            "user_id": "test_user",
            "bot": {
                "bot_user_id": "UTTTTTTTTTTR",
                "bot_access_token": "xoxb-XXXXXXXXXXXX-TTTTTTTTTTTTTT",
            },
        },
    )

    # Act -- oauth callback and token exchange
    state = ""
    code = "1234"
    qs = f"state={state}&code={code}"
    callback_url = f"https://busybeaver.sivji.com/slack/oauth?{qs}"
    slack_verify_callback_and_save_access_tokens_in_database(callback_url, state)

    # Assert -- information in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-XXXXXXXX-XXXXXXXX-XXXXX"
    assert installation.scope == "incoming-webhook,commands,bot"
    assert installation.workspace_name == "Team Installing Your Hook"
    assert installation.workspace_id == "TXXXXXXXXX"
    assert installation.authorizing_user_id == "test_user"
    assert installation.bot_user_id == "UTTTTTTTTTTR"
    assert installation.bot_access_token == "xoxb-XXXXXXXXXXXX-TTTTTTTTTTTTTT"
