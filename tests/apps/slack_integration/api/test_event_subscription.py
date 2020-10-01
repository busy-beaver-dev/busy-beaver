import pytest

from busy_beaver.apps.slack_integration.blocks import AppHome
from busy_beaver.apps.slack_integration.event_subscription import app_home_handler
from busy_beaver.models import (
    CallForProposalsConfiguration,
    GitHubSummaryConfiguration,
    SlackInstallation,
    SlackUser,
    UpcomingEventsConfiguration,
)
from tests._utilities import FakeSlackClient

pytest_plugins = ("tests._utilities.fixtures.slack",)


@pytest.fixture
def patch_slack(patcher):
    def _patch_slack(module_to_patch_slack, *, is_admin=None):
        obj = FakeSlackClient(is_admin=is_admin)
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


class TestDMEventCallback:
    @pytest.mark.integration
    def test_slack_callback_bot_message_is_ignored(
        self, client, session, patch_slack, create_slack_headers
    ):
        """Bot get notified of its own DM replies to users... ignore"""
        # Arrange
        patched_slack = patch_slack(
            "busy_beaver.apps.slack_integration.event_subscription"
        )
        data = {
            "type": "event_callback",
            "event": {"type": "message", "subtype": "bot_message", "user": "my_id"},
        }
        headers = create_slack_headers(100_000_000, data)

        # Act
        resp = client.post("/slack/event-subscription", headers=headers, json=data)

        # Assert
        assert resp.status_code == 200
        assert len(patched_slack.mock.mock_calls) == 0

    @pytest.mark.integration
    def test_slack_callback_user_dms_bot_reply(
        self, client, session, factory, patch_slack, create_slack_headers
    ):
        """When user messages bot, reply with help text"""
        # Arrange
        patched_slack = patch_slack(
            "busy_beaver.apps.slack_integration.event_subscription"
        )
        patch_slack("busy_beaver.apps.slack_integration.interactors", is_admin=True)
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


class TestMemberJoinedChannelEventCallback:
    @pytest.mark.end2end
    def test_user_joins_github_summary_channel_with_feature_enabled(
        self, client, session, factory, patch_slack, create_slack_headers
    ):
        # Arrange
        patched_slack = patch_slack(
            "busy_beaver.apps.slack_integration.event_subscription"
        )
        # Create installation in database
        workspace_id = "TXXXXXXXXX"
        authorizing_user_id = "alysivji"
        bot_id = "test_bot"
        channel = "busy-beaver"
        installation = factory.SlackInstallation(
            authorizing_user_id=authorizing_user_id,
            workspace_id=workspace_id,
            workspace_name="Test",
            bot_user_id=bot_id,
        )
        factory.GitHubSummaryConfiguration(
            enabled=True, channel=channel, slack_installation=installation
        )

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


@pytest.mark.end2end
def test_user_joins_github_summary_channel_with_feature_disabled(
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
        workspace_id=workspace_id,
        workspace_name="Test",
        bot_user_id=bot_id,
    )
    factory.GitHubSummaryConfiguration(
        enabled=False, channel=channel, slack_installation=installation
    )

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

    # Assert -- check that we did not send anything
    assert patched_slack.mock.call_count == 0


class TestAppHomeOpenedEventCallback:
    @pytest.mark.unit
    def test_user_opens_app_home_for_first_time__shown_app_home(
        self, client, session, factory, patch_slack, create_slack_headers
    ):
        # Arrange
        workspace_id = "TXXXXXXXXX"
        user_id = "U5FTQ3QRZ"
        installation = factory.SlackInstallation(workspace_id=workspace_id)
        patched_slack = patch_slack(
            "busy_beaver.apps.slack_integration.event_subscription"
        )

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
        self, client, session, factory, patch_slack, create_slack_headers
    ):
        # Arrange
        workspace_id = "TXXXXXXXXX"
        user_id = "U5FTQ3QRZ"
        installation = factory.SlackInstallation(workspace_id=workspace_id)
        user = factory.SlackUser(slack_id=user_id, installation=installation)
        original_user_count = user.app_home_opened_count
        patched_slack = patch_slack(
            "busy_beaver.apps.slack_integration.event_subscription"
        )

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
        self, client, session, factory, patch_slack, create_slack_headers
    ):
        # Arrange
        workspace_id = "TXXXXXXXXX"
        user_id = "U5FTQ3QRZ"
        factory.SlackInstallation(workspace_id=workspace_id)
        patched_slack = patch_slack(
            "busy_beaver.apps.slack_integration.event_subscription"
        )

        # Act
        data = {
            "type": "event_callback",
            "team_id": workspace_id,
            "event": {"type": "app_home_opened", "user": user_id, "tab": "messages"},
        }
        app_home_handler(data)

        # Assert
        assert patched_slack.mock.assert_not_called


class TestAppUninstalledEventCallback:
    @pytest.mark.integration
    def test_uninstall_application(
        self, client, session, factory, create_slack_headers
    ):
        # Arrange
        workspace_id = "abc"
        installation = factory.SlackInstallation(workspace_id=workspace_id)
        factory.SlackUser(installation=installation)
        factory.CallForProposalsConfiguration(slack_installation=installation)
        factory.GitHubSummaryConfiguration(slack_installation=installation)
        factory.UpcomingEventsConfiguration(slack_installation=installation)

        data = {
            "type": "event_callback",
            "event": {"type": "app_uninstalled"},
            "team_id": workspace_id,
        }
        headers = create_slack_headers(100_000_000, data)

        # Act
        resp = client.post("/slack/event-subscription", headers=headers, json=data)

        # Assert
        assert resp.status_code == 200

        assert SlackInstallation.query.count() == 0
        assert SlackUser.query.count() == 0
        assert CallForProposalsConfiguration.query.count() == 0
        assert UpcomingEventsConfiguration.query.count() == 0
        assert GitHubSummaryConfiguration.query.count() == 0
