import pytest
import responses

from busy_beaver.adapters.slack import TimezoneInfo
from busy_beaver.apps.external_integrations.oauth_providers.slack import SlackOAuthFlow
from busy_beaver.models import GitHubSummaryConfiguration, SlackInstallation
from tests._utilities import FakeSlackClient


@pytest.fixture
def patch_slack(patcher):
    def _patch_slack(module_to_patch_slack, *, timezone_info=None):
        obj = FakeSlackClient(timezone_info=timezone_info)
        patcher(module_to_patch_slack, namespace="SlackAdapter", replacement=obj)
        return obj

    return _patch_slack


@pytest.mark.integration
def test_slack_callback_url_verification(
    client, session, patch_slack, create_slack_headers
):
    # Arrange
    patch_slack("busy_beaver.blueprints.slack.event_subscription")
    challenge_code = "test_code"
    data = {"type": "url_verification", "challenge": challenge_code}
    headers = create_slack_headers(100_000_000, data)

    # Act
    resp = client.post("/slack/event-subscription", headers=headers, json=data)

    # Assert
    assert resp.status_code == 200
    assert resp.json == {"challenge": challenge_code}


@pytest.mark.integration
def test_slack_callback_bot_message_is_ignored(
    mocker, client, session, patch_slack, create_slack_headers
):
    """Bot get notified of its own DM replies to users... ignore"""
    # Arrange
    patched_slack = patch_slack("busy_beaver.blueprints.slack.event_subscription")
    data = {
        "type": "unknown todo",
        "event": {"type": "message", "subtype": "bot_message"},
    }
    headers = create_slack_headers(100_000_000, data)

    # Act
    resp = client.post("/slack/event-subscription", headers=headers, json=data)

    # Assert
    assert resp.status_code == 200
    assert len(patched_slack.mock.mock_calls) == 0


@pytest.mark.integration
def test_slack_callback_user_dms_bot_reply(
    mocker, client, session, factory, patch_slack, create_slack_headers
):
    """When user messages bot, reply with help text"""
    # Arrange
    patched_slack = patch_slack("busy_beaver.blueprints.slack.event_subscription")
    factory.SlackInstallation(workspace_id="team_id")
    channel_id = 5
    data = {
        "type": "event_callback",
        "team_id": "team_id",
        "event": {
            "type": "message",
            "subtype": "not bot_message",
            "channel_type": "im",
            "text": "random",
            "user": "random_user",
            "channel": channel_id,
        },
    }
    headers = create_slack_headers(100_000_000, data)

    # Act
    resp = client.post("/slack/event-subscription", headers=headers, json=data)

    # Assert
    assert resp.status_code == 200
    assert len(patched_slack.mock.mock_calls) == 2
    args, kwargs = patched_slack.mock.call_args
    assert "/busybeaver help" in args[0]
    assert kwargs["channel_id"] == channel_id


@pytest.mark.end2end
@responses.activate
def test_slack_onboarding_install(client, session, patch_slack):
    # Arrange
    # Step 1 -- User goes to 3rd party website and authenticates app
    # Step 2 -- Create response to send back during token exchange
    patched_slack = patch_slack("busy_beaver.apps.external_integrations.workflow")
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
    callback_url = f"/slack/oauth?{qs}"
    client.get(callback_url)

    # Assert -- confirm info in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.access_token == "xoxp-XXXXXXXX-XXXXXXXX-XXXXX"
    assert installation.scope == "incoming-webhook,commands,bot"
    assert installation.workspace_name == "Team Installing Your Hook"
    assert installation.workspace_id == "TXXXXXXXXX"
    assert installation.authorizing_user_id == "test_user"
    assert installation.bot_user_id == "UTTTTTTTTTTR"
    assert installation.bot_access_token == "xoxb-XXXXXXXXXXXX-TTTTTTTTTTTTTT"
    assert installation.state == "user_welcomed"

    # Assert -- check if welcome message was sent
    args, kwargs = patched_slack.mock.call_args
    assert "I recommend creating `#busy-beaver`" in args[0]
    assert "test_user" in kwargs["user_id"]


@pytest.mark.end2end
def test_slack_onboarding_invite_bot_to_channel(
    client, session, factory, patch_slack, create_slack_headers
):
    """TODO deal with situation where bot is invited to multiple channels"""
    # Arrange
    patched_slack = patch_slack("busy_beaver.apps.external_integrations.workflow")
    # Create installation in database
    workspace_id = "TXXXXXXXXX"
    authorizing_user_id = "alysivji"
    bot_id = "test_bot"
    channel = "busy-beaver"
    installation = factory.SlackInstallation(
        authorizing_user_id=authorizing_user_id,
        state="user_welcomed",
        workspace_id=workspace_id,
        workspace_name="Test",
        bot_user_id=bot_id,
    )

    # Act -- event_subscription callback
    data = {
        "type": "event_callback",
        "team_id": workspace_id,
        "event": {
            "type": "member_joined_channel",
            "channel_type": "im",
            "user": bot_id,
            "channel": channel,
        },
    }
    headers = create_slack_headers(100_000_000, data)
    client.post("/slack/event-subscription", headers=headers, json=data)

    # Assert -- confirm info in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.state == "config_requested"

    github_summary_config = GitHubSummaryConfiguration.query.first()
    assert github_summary_config.channel == channel

    # Assert -- check if config request set
    args, kwargs = patched_slack.mock.call_args
    assert "What time should I post" in args[0]
    assert kwargs["user_id"] == authorizing_user_id


@pytest.mark.end2end
def test_slack_onboarding_send_bot_configuration(
    client, session, factory, patch_slack, create_slack_headers
):
    """TODO deal with situation where bad input is sent"""
    # Arrange
    tz = TimezoneInfo(
        tz="America/Chicago", label="Central Daylight Time", offset=-18000
    )
    patched_slack = patch_slack(
        "busy_beaver.apps.external_integrations.workflow", timezone_info=tz
    )
    # Create installation in database
    workspace_id = "TXXXXXXXXX"
    authorizing_user_id = "alysivji"
    bot_id = "test_bot"
    channel = "busy-beaver"
    time_to_post = "2:00pm"
    installation = factory.SlackInstallation(
        authorizing_user_id=authorizing_user_id,
        state="config_requested",
        workspace_id=workspace_id,
        workspace_name="Test",
        bot_user_id=bot_id,
    )
    github_summary_config = factory.GitHubSummaryConfiguration(
        channel=channel, slack_installation=installation
    )

    # Act -- event_subscription callback
    data = {
        "type": "event_callback",
        "team_id": workspace_id,
        "event": {
            "type": "message",
            "channel_type": "im",
            "text": time_to_post,
            "user": authorizing_user_id,
            "channel": channel,
        },
    }
    headers = create_slack_headers(100_000_000, data)
    client.post("/slack/event-subscription", headers=headers, json=data)

    # Assert -- confirm info in database is as expected
    installation = SlackInstallation.query.first()
    assert installation.state == "active"

    github_summary_config = GitHubSummaryConfiguration.query.first()
    assert github_summary_config.channel == channel

    # Assert -- check if config request set
    args, kwargs = patched_slack.mock.call_args
    assert "Busy Beaver is now active!" in args[0]
    assert kwargs["user_id"] == authorizing_user_id
