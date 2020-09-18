import io

import pytest

from busy_beaver.models import (
    SlackInstallation,
    UpcomingEventsConfiguration,
    UpcomingEventsGroup,
)
from tests._utilities import FakeSlackClient

pytest_plugins = ("tests._utilities.fixtures.aws_s3",)
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
    def test_upcoming_events_view_add_new_group_page(
        self, login_client, factory, patch_slack
    ):
        # Arrange
        slack_user = factory.SlackUser()
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)

        # Act
        rv = client.get("/settings/upcoming-events/group", follow_redirects=True)

        # Assert
        assert rv.status_code == 200

    @pytest.mark.end2end
    @pytest.mark.vcr
    def test_upcoming_events_add_new_group__success(
        self, login_client, factory, patch_slack
    ):
        # Arrange
        config = factory.UpcomingEventsConfiguration(enabled=True)
        slack_user = factory.SlackUser(installation=config.slack_installation)
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)

        # Act
        rv = client.post(
            "/settings/upcoming-events/group",
            data={"meetup_urlname": "_CHIPY_"},
            follow_redirects=True,
        )

        # Assert
        assert rv.status_code == 200
        groups = UpcomingEventsGroup.query.all()
        assert len(groups) == 1
        assert groups[0].meetup_urlname == "_ChiPy_"

    @pytest.mark.end2end
    @pytest.mark.vcr
    def test_upcoming_events_add_new_group__does_not_exist(
        self, login_client, factory, patch_slack
    ):
        # Arrange
        config = factory.UpcomingEventsConfiguration(enabled=True)
        slack_user = factory.SlackUser(installation=config.slack_installation)
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)

        # Act
        rv = client.post(
            "/settings/upcoming-events/group",
            data={"meetup_urlname": "adsfasdfeum3n4x"},
            follow_redirects=True,
        )

        # Assert
        assert rv.status_code == 200
        assert b"Group does not exist" in rv.data
        groups = UpcomingEventsGroup.query.all()
        assert len(groups) == 0

    @pytest.mark.end2end
    @pytest.mark.vcr
    def test_upcoming_events_add_new_group__group_already_added(
        self, login_client, factory, patch_slack
    ):
        # Arrange
        config = factory.UpcomingEventsConfiguration(enabled=True)
        UpcomingEventsGroup(meetup_urlname="_ChiPy_", configuration=config)
        slack_user = factory.SlackUser(installation=config.slack_installation)
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)

        # Act
        rv = client.post(
            "/settings/upcoming-events/group",
            data={"meetup_urlname": "_ChiPy_"},
            follow_redirects=True,
        )

        # Assert
        assert rv.status_code == 200
        assert b"Group already added" in rv.data
        groups = UpcomingEventsGroup.query.all()
        assert len(groups) == 1

    @pytest.mark.end2end
    @pytest.mark.parametrize("start_state,end_state", [(True, False), (False, True)])
    def test_upcoming_events_toggle_enabled_status(
        self, login_client, factory, patch_slack, start_state, end_state
    ):
        # Arrange
        config = factory.UpcomingEventsConfiguration(enabled=True)
        slack_user = factory.SlackUser(installation=config.slack_installation)
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)

        # Act
        rv = client.get("/settings/upcoming-events/toggle", follow_redirects=True)

        # Assert
        assert rv.status_code == 200

        config = UpcomingEventsConfiguration.query.get(config.id)
        assert config.enabled is False

    @pytest.mark.end2end
    def test_upcoming_events_delete(self, login_client, factory, patch_slack):
        # Arrange
        config = factory.UpcomingEventsConfiguration(enabled=True)
        group = UpcomingEventsGroup(meetup_urlname="_ChiPy_", configuration=config)
        slack_user = factory.SlackUser(installation=config.slack_installation)
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)

        # Act
        rv = client.get(
            f"/settings/upcoming-events/group/{group.id}/delete", follow_redirects=True
        )

        # Assert
        assert rv.status_code == 200
        groups = UpcomingEventsGroup.query.all()
        assert len(groups) == 0

    @pytest.mark.end2end
    @pytest.mark.parametrize("start_state,end_state", [(True, False), (False, True)])
    def test_toggle_post_cron_view(
        self, login_client, factory, patch_slack, start_state, end_state
    ):
        # Arrange
        config = factory.UpcomingEventsConfiguration(post_cron_enabled=start_state)
        slack_user = factory.SlackUser(installation=config.slack_installation)
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)

        # Act
        rv = client.get(
            "/settings/upcoming-events/post-cron/toggle", follow_redirects=True
        )

        # Assert
        assert rv.status_code == 200

        config = UpcomingEventsConfiguration.query.get(config.id)
        assert config.post_cron_enabled is end_state


class TestUpdateWorkspaceLogoview:
    @pytest.mark.end2end
    def test_organization_settings(self, s3, login_client, factory, patch_slack):
        # Arrange
        slack_user = factory.SlackUser()
        client = login_client(user=slack_user)
        patch_slack(is_admin=True)
        logo_bytes = b"abcdefghijklmnopqrstuvwxyz"
        logo_file = io.BytesIO(logo_bytes)

        # Act
        rv = client.post(
            "/settings/organization",
            data={
                "organization_name": "Chicago Python",
                "logo": (logo_file, "testfile.txt"),
            },
            follow_redirects=True,
            content_type="multipart/form-data",
        )

        # Assert
        assert rv.status_code == 200
        installation = SlackInstallation.query.first()
        assert installation.organization_name == "Chicago Python"
        assert ".txt" in installation.workspace_logo_url
