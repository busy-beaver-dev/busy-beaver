import pytest
import responses

from busy_beaver.apps.slack_integration.oauth.oauth_flow import SlackOAuthFlow
from busy_beaver.models import SlackInstallation
from tests._utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.apps.slack_integration.oauth.workflow"


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
            "ok": True,
            "access_token": "xoxb-17653672481-19874698323-pdFZKVeTuE8sk7oOcBrzbqgy",
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
    slack = patched_slack

    # Act -- oauth callback and token exchange
    state = ""
    code = "1234"
    qs = f"state={state}&code={code}"
    resp = client.get(f"/slack/oauth?{qs}")
    assert resp.status_code == 200

    # Assert -- information in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-1234"
    assert installation.scope == "commands,incoming-webhook"
    assert installation.workspace_name == "Slack Softball Team"
    assert installation.workspace_id == "T9TK3CUKW"
    assert installation.authorizing_user_id == "U1234"
    assert installation.bot_user_id == "U0KRQLJ9H"
    assert (
        installation.bot_access_token
        == "xoxb-17653672481-19874698323-pdFZKVeTuE8sk7oOcBrzbqgy"
    )

    # assert things in slack adapter
    assert installation.state == "user_welcomed"

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "To get started" in args[0]
    assert kwargs["user_id"] == "U1234"
