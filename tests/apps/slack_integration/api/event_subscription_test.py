import pytest
import responses

from busy_beaver.apps.slack_integration.blocks import AppHome
from busy_beaver.apps.slack_integration.event_subscription import app_home_handler
from busy_beaver.apps.slack_integration.oauth.oauth_flow import (
    SlackInstallationOAuthFlow,
)
from busy_beaver.common.wrappers.slack import TimezoneInfo
from busy_beaver.models import GitHubSummaryConfiguration, SlackInstallation, SlackUser
from tests._utilities import FakeSlackClient

pytest_plugins = ("tests._utilities.fixtures.slack",)


@pytest.fixture
def patch_slack(patcher):
    def _patch_slack(module_to_patch_slack, *, timezone_info=None):
        obj = FakeSlackClient(timezone_info=timezone_info)
        patcher(module_to_patch_slack, namespace="SlackClient", replacement=obj)
        return obj

    return _patch_slack


@pytest.mark.integration
def test_slack_callback_url_verification(
    client, session, patch_slack, create_slack_headers
):
    # Arrange
    patch_slack("busy_beaver.apps.slack_integration.event_subscription")
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
    patched_slack = patch_slack("busy_beaver.apps.slack_integration.event_subscription")
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
    patched_slack = patch_slack("busy_beaver.apps.slack_integration.event_subscription")
    factory.SlackInstallation(workspace_id="team_id")
    channel = 5
    data = {
        "type": "event_callback",
        "team_id": "team_id",
        "event": {
            "type": "message",
            "subtype": "not bot_message",
            "channel_type": "im",
            "text": "random",
            "user": "random_user",
            "channel": channel,
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
    assert kwargs["channel"] == channel


@pytest.mark.end2end
@responses.activate
def test_slack_onboarding_install(client, session, patch_slack):
    # Arrange
    # Step 1 -- User goes to 3rd party website and authenticates app
    # Step 2 -- Create response to send back during token exchange
    patched_slack = patch_slack("busy_beaver.apps.slack_integration.oauth.workflow")
    responses.add(
        responses.POST,
        SlackInstallationOAuthFlow.TOKEN_URL,
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

    # Act -- oauth callback and token exchange
    state = ""
    code = "1234"
    qs = f"state={state}&code={code}"
    callback_url = f"/slack/oauth?{qs}"
    client.get(callback_url)

    # Assert -- confirm info in database is as expected
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
    assert installation.state == "user_welcomed"

    # Assert -- check if welcome message was sent
    args, kwargs = patched_slack.mock.call_args
    assert "I recommend creating `#busy-beaver`" in args[0]
    assert "U1234" in kwargs["user_id"]


@pytest.mark.end2end
def test_slack_onboarding_invite_bot_to_channel(
    client, session, factory, patch_slack, create_slack_headers
):
    """TODO deal with situation where bot is invited to multiple channels"""
    # Arrange
    patched_slack = patch_slack("busy_beaver.apps.slack_integration.oauth.workflow")
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
        "busy_beaver.apps.slack_integration.oauth.workflow", timezone_info=tz
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


@pytest.mark.end2end
def test_user_joins_github_summary_channel(
    client, session, factory, patch_slack, create_slack_headers
):
    # Arrange
    patched_slack = patch_slack("busy_beaver.apps.slack_integration.event_subscription")
    # Create installation in database
    workspace_id = "TXXXXXXXXX"
    authorizing_user_id = "alysivji"
    bot_id = "test_bot"
    channel = "busy-beaver"
    installation = factory.SlackInstallation(
        authorizing_user_id=authorizing_user_id,
        state="active",
        workspace_id=workspace_id,
        workspace_name="Test",
        bot_user_id=bot_id,
    )
    factory.GitHubSummaryConfiguration(channel=channel, slack_installation=installation)

    # Act -- event_subscription callback
    data = {
        "type": "event_callback",
        "team_id": workspace_id,
        "event": {
            "type": "member_joined_channel",
            "user": authorizing_user_id,
            "channel": channel,
        },
    }
    headers = create_slack_headers(100_000_000, data)
    client.post("/slack/event-subscription", headers=headers, json=data)

    # Assert -- check that we send ephhermal message
    args, kwargs = patched_slack.mock.call_args
    assert "/busybeaver connect" in args[0]
    assert kwargs["user_id"] == authorizing_user_id


@pytest.mark.unit
def test_user_opens_app_home_for_first_time__shown_app_home(
    client, session, factory, patch_slack, create_slack_headers
):
    # Arrange
    workspace_id = "TXXXXXXXXX"
    user_id = "U5FTQ3QRZ"
    installation = factory.SlackInstallation(workspace_id=workspace_id)
    patched_slack = patch_slack("busy_beaver.apps.slack_integration.event_subscription")

    # Act
    data = {
        "type": "event_callback",
        "team_id": workspace_id,
        "event": {"type": "app_home_opened", "user": user_id, "tab": "home"},
    }
    app_home_handler(data)

    # Assert -- check we send the app home send
    args, kwargs = patched_slack.mock.call_args
    assert args[0] == user_id
    assert kwargs.get("view", {}) == AppHome().to_dict()

    params = {"installation_id": installation.id, "slack_id": user_id}
    user = SlackUser.query.filter_by(**params).first()
    assert user
    assert user.app_home_opened_count == 1


@pytest.mark.unit
def test_user_opens_app_home_for_greater_than_first_time__shown_app_home(
    client, session, factory, patch_slack, create_slack_headers
):
    # Arrange
    workspace_id = "TXXXXXXXXX"
    user_id = "U5FTQ3QRZ"
    installation = factory.SlackInstallation(workspace_id=workspace_id)
    user = factory.SlackUser(slack_id=user_id, installation=installation)
    original_user_count = user.app_home_opened_count
    patched_slack = patch_slack("busy_beaver.apps.slack_integration.event_subscription")

    # Act
    data = {
        "type": "event_callback",
        "team_id": workspace_id,
        "event": {"type": "app_home_opened", "user": user_id, "tab": "home"},
    }
    app_home_handler(data)

    # Assert -- check we send the app home send
    args, kwargs = patched_slack.mock.call_args
    assert args[0] == user_id
    assert kwargs.get("view", {}) == AppHome().to_dict()

    params = {"installation_id": installation.id, "slack_id": user_id}
    user = SlackUser.query.filter_by(**params).first()
    assert user
    assert user.app_home_opened_count == original_user_count + 1


@pytest.mark.unit
def test_user_opens_app_home_message_tab__does_nothing(
    client, session, factory, patch_slack, create_slack_headers
):
    # Arrange
    workspace_id = "TXXXXXXXXX"
    user_id = "U5FTQ3QRZ"
    factory.SlackInstallation(workspace_id=workspace_id)
    patched_slack = patch_slack("busy_beaver.apps.slack_integration.event_subscription")

    # Act
    data = {
        "type": "event_callback",
        "team_id": workspace_id,
        "event": {"type": "app_home_opened", "user": user_id, "tab": "messages"},
    }
    app_home_handler(data)

    # Assert
    assert patched_slack.mock.assert_not_called
