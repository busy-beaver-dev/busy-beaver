import pytest

from busy_beaver.models import UpcomingEventsConfiguration
from tests._utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.apps.web.views"


@pytest.fixture
def patch_slack(patcher):
    def _patch_slack(*, is_admin=None):
        obj = FakeSlackClient(is_admin=is_admin)
        patcher(MODULE_TO_TEST, namespace="SlackClient", replacement=obj)
        return obj

    return _patch_slack


@pytest.mark.unit
def test_index(client):
    rv = client.get("/")
    assert rv.status_code == 200


class TestAuthentication:
    @pytest.mark.unit
    def test_access_restricted_view(self, client):
        rv = client.get("/settings", follow_redirects=True)
        assert rv.status_code == 200
        assert "slack.com/oauth/v2/authorize" in rv.data.decode("utf-8")

    @pytest.mark.unit
    def test_login_and_access_restricted_view(self, login_client, factory):
        slack_user = factory.SlackUser()
        client = login_client(user=slack_user)

        rv = client.get("/settings", follow_redirects=True)
        assert rv.status_code == 200

    @pytest.mark.unit
    def test_logout_view(self, login_client, factory):
        # Arrange
        slack_user = factory.SlackUser()
        client = login_client(user=slack_user)
        client.get("/logout", follow_redirects=True)

        # Act
        rv = client.get("/settings", follow_redirects=True)

        # Assert
        assert rv.status_code == 200
        assert "slack.com/oauth/v2/authorize" in rv.data.decode("utf-8")


class TestUpcomingEventsViews:
    @pytest.mark.end2end
    def test_upcoming_events_get(self, login_client, factory, patch_slack):
        # Arrange
        slack_user = factory.SlackUser()
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)

        # Act
        rv = client.get("/settings/upcoming-events", follow_redirects=True)

        # Assert
        assert rv.status_code == 200

    @pytest.mark.end2end
    def test_upcoming_events_add_new_group(self, login_client, factory, patch_slack):
        # Arrange
        slack_user = factory.SlackUser()
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)

        # Act
        rv = client.get("/settings/upcoming-events/group", follow_redirects=True)

        # Assert
        assert rv.status_code == 200

    @pytest.mark.end2end
    @pytest.mark.current
    def test_upcoming_events_toggle_enabled_status(
        self, login_client, factory, patch_slack
    ):
        # Arrange
        upcoming_events_config = factory.UpcomingEventsConfiguration(enabled=True)
        slack_user = factory.SlackUser(
            installation=upcoming_events_config.slack_installation
        )
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)

        # Act)
        rv = client.get("/settings/upcoming-events/toggle", follow_redirects=True)

        # Assert
        assert rv.status_code == 200

        config = UpcomingEventsConfiguration.query.get(upcoming_events_config.id)
        assert config.enabled is False
