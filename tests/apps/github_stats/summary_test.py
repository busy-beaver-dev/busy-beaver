from datetime import timedelta

from busy_beaver.apps.github_summary.summary import GitHubUserEvents
from busy_beaver.toolbox import utc_now_minus

import pytest


# TODO make freze_time into a test helper that pulls from the cassette directly
@pytest.mark.vcr()
@pytest.mark.freeze_time("2019-01-05")
def test_generate_summary(session, factory):
    # Arrange
    user = factory.GitHubSummaryUser(slack_id="alysivji", github_username="alysivji")
    user_events = GitHubUserEvents(user, utc_now_minus(timedelta(days=1)))

    # Act
    summary = user_events.generate_summary_text()

    assert "alysivji" in summary


@pytest.mark.vcr()
@pytest.mark.freeze_time("2019-06-20")
def test_generates_empty_summary_if_no_events_found(session, factory):
    # Arrange
    user = factory.GitHubSummaryUser(
        slack_id="raymondberg", github_username="raymondberg"
    )
    user_events = GitHubUserEvents(user, utc_now_minus(timedelta(days=1)))

    # Act
    summary = user_events.generate_summary_text()

    assert summary == ""
