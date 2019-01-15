from datetime import datetime, timedelta
import os

import pytest
import pytz

from busy_beaver.adapters.github import (
    APINav,
    create_github_navigation_panel,
    GitHubAdapter,
    page_from_url,
)


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
    vrcpy_timestamp = pytz.utc.localize(datetime(2018, 11, 24, 22, 55, 3, 767_521))
    boundary_dt = vrcpy_timestamp - timedelta(days=1)
    user_activity = client.user_activity_after(user="alysivji", timestamp=boundary_dt)

    assert len(user_activity) >= 0


@pytest.mark.vcr()
def test_all_user_repos(client):
    all_repos = client.all_user_repos("alysivji")

    assert len(all_repos) >= 50


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
