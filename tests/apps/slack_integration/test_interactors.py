import pytest

from busy_beaver.apps.slack_integration.interactors import generate_help_text
from tests._utilities import FakeSlackClient

pytest_plugins = ("tests._utilities.fixtures.slack",)
MODULE_TO_TEST = "busy_beaver.apps.slack_integration.interactors"


@pytest.fixture
def patch_slack(patcher):
    def _patch_slack(*, is_admin=None):
        obj = FakeSlackClient(is_admin=is_admin)
        patcher(MODULE_TO_TEST, namespace="SlackClient", replacement=obj)
        return obj

    return _patch_slack


class TestGenerateHelpText:
    @pytest.mark.unit
    def test_all_features_disabled(self, client, session, factory, patch_slack):
        user = factory.SlackUser()
        installation = user.installation
        factory.UpcomingEventsConfiguration(
            slack_installation=installation, enabled=False
        )
        factory.GitHubSummaryConfiguration(
            slack_installation=installation, enabled=False
        )
        patch_slack(is_admin=True)

        help_text = generate_help_text(installation, user.slack_id)

        assert "/busybeaver help" in help_text
        assert "/busybeaver connect" not in help_text
        assert "/busybeaver events" not in help_text

    @pytest.mark.unit
    def test_github_summary_enabled(self, client, session, factory, patch_slack):
        user = factory.SlackUser()
        installation = user.installation
        factory.GitHubSummaryConfiguration(
            slack_installation=installation, enabled=True
        )
        factory.UpcomingEventsConfiguration(
            slack_installation=installation, enabled=False
        )
        patch_slack(is_admin=True)

        help_text = generate_help_text(installation, user.slack_id)

        assert "/busybeaver help" in help_text
        assert "/busybeaver connect" in help_text
        assert "/busybeaver events" not in help_text

    @pytest.mark.unit
    def test_upcoming_events_enabled(self, client, session, factory, patch_slack):
        user = factory.SlackUser()
        installation = user.installation
        factory.GitHubSummaryConfiguration(
            slack_installation=installation, enabled=False
        )
        factory.UpcomingEventsConfiguration(
            slack_installation=installation, enabled=True
        )
        patch_slack(is_admin=True)

        help_text = generate_help_text(installation, user.slack_id)

        assert "/busybeaver help" in help_text
        assert "/busybeaver connect" not in help_text
        assert "/busybeaver events" in help_text

    @pytest.mark.unit
    @pytest.mark.parametrize("is_admin, matches", [(False, False), (True, True)])
    def test_show_settings_for_admins(
        self, client, session, factory, patch_slack, is_admin, matches
    ):
        user = factory.SlackUser()
        installation = user.installation
        factory.GitHubSummaryConfiguration(
            slack_installation=installation, enabled=False
        )
        factory.UpcomingEventsConfiguration(
            slack_installation=installation, enabled=True
        )
        patch_slack(is_admin=is_admin)

        help_text = generate_help_text(installation, user.slack_id)

        assert ("/busybeaver settings" in help_text) is matches
