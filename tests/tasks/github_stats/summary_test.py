from datetime import timedelta

from busy_beaver.tasks.github_stats.summary import generate_summary
from busy_beaver.toolbox import utc_now_minus

import pytest


# TODO make freze_time into a test helper that pulls from the cassette directly
@pytest.mark.vcr()
@pytest.mark.freeze_time("2019-01-05")
def test_generate_summary(create_user):
    user = create_user("alysivji")

    assert "alysivji" in generate_summary(user, utc_now_minus(timedelta(days=1)))


# TODO add a lot more tests
