from urllib.parse import parse_qs, urlparse

import pytest
import responses

from busy_beaver.apps.external_integrations.oauth_providers.slack import SlackOAuthFlow
from busy_beaver.apps.external_integrations.workflow import (
    slack_generate_and_save_auth_tuple,
    slack_verify_callback_and_save_access_tokens_in_database,
)
from busy_beaver.models import SlackInstallation


@pytest.mark.integration
@responses.activate
def test_slack_oauth_flow_first_time_installation(session):
    # Step 1
    # generation installation link and direction
    auth = slack_generate_and_save_auth_tuple()
    assert SlackOAuthFlow.AUTHORIZATION_BASE_URL in auth.url
    state = auth.state

    # Step 2
    # User goes to 3rd party website and authenticates app

    # Step 3
    # create response to send back during token exchange
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

    # Step 4
    # oauth callback and token exchange
    code = "1234"
    qs = f"state={state}&code={code}"
    callback_url = f"https://busybeaver.sivji.com/slack/oauth?{qs}"
    slack_verify_callback_and_save_access_tokens_in_database(callback_url, state)

    # Step 5
    # assert information in database is as expected
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
def test_slack_oauth_flow_reinstallation(session):
    workspace_id = "TXXXXXXXXX"

    # Step 1
    # create installation in database
    installation = SlackInstallation(workspace_id=workspace_id, workspace_name="Test")
    session.add(installation)
    session.commit()

    # Step 2
    # generation installation link and direction
    auth = slack_generate_and_save_auth_tuple()
    assert SlackOAuthFlow.AUTHORIZATION_BASE_URL in auth.url
    redirect_url = auth.url
    state = auth.state

    # Step 3
    # User goes to 3rd party website and authenticates us

    # Step 4
    # get code so we can generate a callback url to hit our endpoint
    parsed_redirect_url = urlparse(redirect_url)
    parsed_query_string = parse_qs(parsed_redirect_url.query)
    assert "state" in parsed_query_string
    state = parsed_query_string["state"][0]

    # Step 5
    # create response to send back during token exchange
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

    # Step 6
    # oauth callback and token exchange
    code = "1234"
    qs = f"state={state}&code={code}"
    callback_url = f"https://busybeaver.sivji.com/slack/oauth?{qs}"
    slack_verify_callback_and_save_access_tokens_in_database(callback_url, state)

    # Step 7
    # assert information in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-XXXXXXXX-XXXXXXXX-XXXXX"
    assert installation.scope == "incoming-webhook,commands,bot"
    assert installation.workspace_name == "Team Installing Your Hook"
    assert installation.workspace_id == "TXXXXXXXXX"
    assert installation.authorizing_user_id == "test_user"
    assert installation.bot_user_id == "UTTTTTTTTTTR"
    assert installation.bot_access_token == "xoxb-XXXXXXXXXXXX-TTTTTTTTTTTTTT"
