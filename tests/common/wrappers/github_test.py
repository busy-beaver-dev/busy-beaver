from datetime import datetime, timedelta

import pytest
import pytz
from dateutil.parser import parse as parse_dt

from busy_beaver.common.wrappers.github import (
    APINav,
    GitHubClient,
    create_github_navigation_panel,
    page_from_url,
)
from busy_beaver.config import GITHUB_OAUTH_TOKEN


@pytest.fixture
def client():
    yield GitHubClient(oauth_token=GITHUB_OAUTH_TOKEN)


@pytest.mark.vcr()
def test_all_user_stars(client):
    starred_repos = client.all_user_stars(user="alysivji", max_pages=4)

    assert len(starred_repos) == 120


@pytest.mark.vcr()
def test_all_user_activity_after(client):
    # TODO don't like how I hardcoded date, think of more robust solution
    vrcpy_timestamp = pytz.utc.localize(datetime(2018, 11, 24, 22, 55, 3, 767_521))
    boundary_dt = vrcpy_timestamp - timedelta(days=1)
    user_activity = client.user_activity_after(user="alysivji", timestamp=boundary_dt)

    assert len(user_activity) >= 0


@pytest.mark.vcr()
@pytest.mark.freeze_time("2020-01-13")
def test_user_activity_during_range(client):
    # Arrange
    start_dt = pytz.utc.localize(datetime.utcnow())
    end_dt = start_dt + timedelta(days=1)

    # Act
    user_activity = client.user_activity_during_range(
        user="alysivji", start_dt=start_dt, end_dt=end_dt
    )

    # Assert
    assert len(user_activity) >= 0
    for event in user_activity:
        assert start_dt <= parse_dt(event["created_at"]) <= end_dt


@pytest.mark.vcr()
def test_all_user_repos(client):
    all_repos = client.all_user_repos("alysivji")

    assert len(all_repos) >= 50


@pytest.mark.vcr()
def test_user_details(client):
    details = client.user_details()

    assert details["login"] == "alysivji"


@pytest.mark.unit
def test_parsing_header_links():
    # Arrange
    link_header = (
        '<https://api.github.com/user/4369343/events/public?page=3>; rel="next", '
        '<https://api.github.com/user/4369343/events/public?page=10>; rel="last", '
        '<https://api.github.com/user/4369343/events/public?page=1>; rel="prev", '
        '<https://api.github.com/user/4369343/events/public?page=1>; rel="first"'
    )

    # Act
    links = create_github_navigation_panel(link_header)

    # Assert
    expected = APINav(
        first_link="https://api.github.com/user/4369343/events/public?page=1",
        prev_link="https://api.github.com/user/4369343/events/public?page=1",
        next_link="https://api.github.com/user/4369343/events/public?page=3",
        last_link="https://api.github.com/user/4369343/events/public?page=10",
    )
    assert links == expected


@pytest.mark.unit
def test_parsing_header_links_empty():
    # Arrange
    link_header = ""

    # Act
    # Assert
    with pytest.raises(ValueError):
        create_github_navigation_panel(link_header)


@pytest.mark.parametrize(
    "url, expected_page_num",
    [
        ("https://api.github.com/user/4369343/events/public?page=1", 1),
        ("https://api.github.com/user/4369343/events/public?page=3", 3),
        ("https://api.github.com/user/4369343/events/public?page=10", 10),
    ],
)
def test_page_from_url(url, expected_page_num):
    # Act
    result = page_from_url(url)

    # Assert
    assert result == expected_page_num
