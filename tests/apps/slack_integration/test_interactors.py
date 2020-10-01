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


@pytest.mark.unit
def test_generate_help_text_all_features_disabled(
    client, session, factory, patch_slack
):
    user = factory.SlackUser()
    installation = user.installation
    factory.UpcomingEventsConfiguration(slack_installation=installation, enabled=False)
    factory.GitHubSummaryConfiguration(slack_installation=installation, enabled=False)
    patch_slack(is_admin=True)

    help_text = generate_help_text(installation, user.slack_id)

    assert "/busybeaver help" in help_text
    assert "/busybeaver connect" not in help_text
    assert "/busybeaver events" not in help_text


@pytest.mark.unit
def test_generate_help_text_github_summary_enabled(
    client, session, factory, patch_slack
):
    user = factory.SlackUser()
    installation = user.installation
    factory.GitHubSummaryConfiguration(slack_installation=installation, enabled=True)
    factory.UpcomingEventsConfiguration(slack_installation=installation, enabled=False)
    patch_slack(is_admin=True)

    help_text = generate_help_text(installation, user.slack_id)

    assert "/busybeaver help" in help_text
    assert "/busybeaver connect" in help_text
    assert "/busybeaver events" not in help_text


@pytest.mark.unit
def test_generate_help_text_upcoming_events_enabled(
    client, session, factory, patch_slack
):
    user = factory.SlackUser()
    installation = user.installation
    factory.GitHubSummaryConfiguration(slack_installation=installation, enabled=False)
    factory.UpcomingEventsConfiguration(slack_installation=installation, enabled=True)
    patch_slack(is_admin=True)

    help_text = generate_help_text(installation, user.slack_id)

    assert "/busybeaver help" in help_text
    assert "/busybeaver connect" not in help_text
    assert "/busybeaver events" in help_text
