from datetime import timedelta

from busy_beaver.tasks.github_stats.summary import GitHubUserEvents
from busy_beaver.toolbox import utc_now_minus

import pytest


# TODO make freze_time into a test helper that pulls from the cassette directly
@pytest.mark.vcr()
@pytest.mark.freeze_time("2019-01-05")
def test_generate_summary(create_user):
    # Arrange
    user = create_user("alysivji")
    user_events = GitHubUserEvents(user, utc_now_minus(timedelta(days=1)))

    # Act
    summary = user_events.generate_summary_text()

    assert "alysivji" in summary


# TODO add a lot more tests
