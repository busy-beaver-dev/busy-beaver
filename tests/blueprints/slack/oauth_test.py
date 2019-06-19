from urllib.parse import parse_qs, urlparse

import pytest
import responses

from busy_beaver.apps.external_integrations.oauth_providers.slack import SlackOAuthFlow
from busy_beaver.models import SlackInstallation


@pytest.mark.end2end
@responses.activate
def test_slack_oauth_flow_happy_path(client, session):
    # Step 1
    # generation installation link and direction
    resp = client.get("/slack/install")
    redirect_url = resp.location
    assert SlackOAuthFlow.AUTHORIZATION_BASE_URL in redirect_url

    # Step 2
    # User goes to 3rd party website and authenticates us

    # Step 3
    # get code so we can generate a callback url to hit our endpoint
    parsed_redirect_url = urlparse(redirect_url)
    parsed_query_string = parse_qs(parsed_redirect_url.query)
    assert "state" in parsed_query_string
    state = parsed_query_string["state"][0]

    # Step 4
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

    # Step 5
    # oauth callback and token exchange
    code = "1234"
    qs = f"state={state}&code={code}"
    resp = client.get(f"/slack/oauth?{qs}")
    assert resp.status_code == 200

    # Step 6
    # assert information in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-XXXXXXXX-XXXXXXXX-XXXXX"
    assert installation.scope == "incoming-webhook,commands,bot"
    assert installation.workspace_name == "Team Installing Your Hook"
    assert installation.workspace_id == "TXXXXXXXXX"
    assert installation.authorizing_user_id == "test_user"
    assert installation.bot_user_id == "UTTTTTTTTTTR"
    assert installation.bot_access_token == "xoxb-XXXXXXXXXXXX-TTTTTTTTTTTTTT"
