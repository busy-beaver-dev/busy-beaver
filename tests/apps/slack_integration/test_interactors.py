import pytest

from busy_beaver.apps.slack_integration.interactors import generate_help_text

pytest_plugins = ("tests._utilities.fixtures.slack",)


@pytest.mark.unit
def test_generate_help_text_all_features_disabled(
    client, session, factory, create_slack_headers, generate_slash_command_request
):
    installation = factory.SlackInstallation()
    factory.UpcomingEventsConfiguration(slack_installation=installation, enabled=False)
    factory.GitHubSummaryConfiguration(slack_installation=installation, enabled=False)

    help_text = generate_help_text(installation)

    assert "/busybeaver help" in help_text
    assert "/busybeaver connect" not in help_text
    assert "/busybeaver events" not in help_text


@pytest.mark.unit
def test_generate_help_text_github_summary_enabled(
    client, session, factory, create_slack_headers, generate_slash_command_request
):
    installation = factory.SlackInstallation()
    factory.GitHubSummaryConfiguration(slack_installation=installation, enabled=True)
    factory.UpcomingEventsConfiguration(slack_installation=installation, enabled=False)

    help_text = generate_help_text(installation)

    assert "/busybeaver help" in help_text
    assert "/busybeaver connect" in help_text
    assert "/busybeaver events" not in help_text


@pytest.mark.unit
def test_generate_help_text_upcoming_events_enabled(
    client, session, factory, create_slack_headers, generate_slash_command_request
):
    installation = factory.SlackInstallation()
    factory.GitHubSummaryConfiguration(slack_installation=installation, enabled=False)
    factory.UpcomingEventsConfiguration(slack_installation=installation, enabled=True)

    help_text = generate_help_text(installation)

    assert "/busybeaver help" in help_text
    assert "/busybeaver connect" not in help_text
    assert "/busybeaver events" in help_text
