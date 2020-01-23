import pytest
import responses

from busy_beaver.apps.oauth_integrations.oauth_providers.slack import SlackOAuthFlow
from busy_beaver.models import SlackInstallation
from tests._utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.apps.oauth_integrations.workflow"


@pytest.fixture
def patched_slack(patcher):
    obj = FakeSlackClient()
    return patcher(MODULE_TO_TEST, namespace="SlackAdapter", replacement=obj)


@pytest.mark.end2end
@responses.activate
def test_slack_oauth_endpoints(client, session, patched_slack):
    # Arrange
    # Step 1 -- User goes to 3rd party website and authenticates us
    # Step 2 -- create response to send back during token exchange
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
    slack = patched_slack

    # Act -- oauth callback and token exchange
    state = ""
    code = "1234"
    qs = f"state={state}&code={code}"
    resp = client.get(f"/slack/oauth?{qs}")
    assert resp.status_code == 200

    # Assert -- information in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-XXXXXXXX-XXXXXXXX-XXXXX"
    assert installation.scope == "incoming-webhook,commands,bot"
    assert installation.workspace_name == "Team Installing Your Hook"
    assert installation.workspace_id == "TXXXXXXXXX"
    assert installation.authorizing_user_id == "test_user"
    assert installation.bot_user_id == "UTTTTTTTTTTR"
    assert installation.bot_access_token == "xoxb-XXXXXXXXXXXX-TTTTTTTTTTTTTT"

    # assert things in slack adapter
    assert installation.state == "user_welcomed"

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "To get started" in args[0]
    assert kwargs["user_id"] == "test_user"
