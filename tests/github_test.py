from datetime import datetime, timedelta
import os

import pytest
import pytz

from adapters.github import GitHubAdapter


@pytest.fixture
def client():
    oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")
    yield GitHubAdapter(oauth_token)


@pytest.mark.vcr()
def test_all_user_stars(client):
    starred_repos = client.all_user_stars(user="alysivji", max_pages=4)

    assert len(starred_repos) == 120


@pytest.mark.vcr()
def test_all_user_activity_after(client):
    # TODO don't like how I hardcoded date, think of more robust solution
    vrcpy_timestamp = pytz.utc.localize(datetime(2018, 11, 24, 22, 55, 3, 767521))
    boundary_dt = vrcpy_timestamp - timedelta(days=1)
    user_activity = client.user_activity_after(user="alysivji", timestamp=boundary_dt)

    assert len(user_activity) >= 0


@pytest.mark.vcr()
def test_all_user_repos(client):
    all_repos = client.all_user_repos("alysivji")

    assert len(all_repos) >= 50
