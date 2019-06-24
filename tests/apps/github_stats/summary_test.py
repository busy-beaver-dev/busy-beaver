from datetime import timedelta

from busy_beaver.apps.github_summary.summary import GitHubUserEvents
from busy_beaver.toolbox import utc_now_minus

import pytest


# TODO make freze_time into a test helper that pulls from the cassette directly
@pytest.mark.vcr()
@pytest.mark.freeze_time("2019-01-05")
def test_generate_summary(create_slack_installation, create_user):
    # Arrange
    slack_install = create_slack_installation(workspace_id="abc")
    user = create_user(
        slack_id="alysivji",
        github_username="alysivji",
        installation_id=slack_install.id,
    )
    user_events = GitHubUserEvents(user, utc_now_minus(timedelta(days=1)))

    # Act
    summary = user_events.generate_summary_text()

    assert "alysivji" in summary


@pytest.mark.vcr()
@pytest.mark.freeze_time("2019-06-20")
def test_generates_empty_summary_if_no_events_found(
    create_slack_installation, create_user
):
    # Arrange
    slack_install = create_slack_installation(workspace_id="abc")
    user = create_user(
        slack_id="raymondberg",
        github_username="raymondberg",
        installation_id=slack_install.id,
    )
    user_events = GitHubUserEvents(user, utc_now_minus(timedelta(days=1)))

    # Act
    summary = user_events.generate_summary_text()

    assert summary == ""
