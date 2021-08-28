from datetime import datetime, timedelta

from dateutil.parser import parse as parse_dt
import pytest
import pytz

from busy_beaver.common.wrappers.github import (
    ApiNav,
    AsyncGitHubClient,
    GitHubClient,
    page_from_url,
)
from busy_beaver.config import GITHUB_OAUTH_TOKEN
from busy_beaver.toolbox import generate_range_utc_now_minus


@pytest.fixture
def github_client():
    yield GitHubClient(oauth_token=GITHUB_OAUTH_TOKEN)


@pytest.fixture
def async_github_client():
    yield AsyncGitHubClient(oauth_token=GITHUB_OAUTH_TOKEN)


class TestGitHubClient:
    @pytest.mark.vcr()
    def test_all_user_stars(self, github_client):
        starred_repos = github_client.all_user_stars(user="alysivji", max_pages=4)

        assert len(starred_repos) == 120

    @pytest.mark.vcr()
    def test_all_user_activity_after(self, github_client):
        # TODO don't like how I hardcoded date, think of more robust solution
        vrcpy_timestamp = pytz.utc.localize(datetime(2018, 11, 24, 22, 55, 3, 767_521))
        boundary_dt = vrcpy_timestamp - timedelta(days=1)
        user_activity = github_client.user_activity_after(
            user="alysivji", timestamp=boundary_dt
        )

        assert len(user_activity) >= 0

    @pytest.mark.vcr()
    @pytest.mark.freeze_time("2020-01-13")
    def test_user_activity_during_range(self, github_client):
        # Arrange
        start_dt = pytz.utc.localize(datetime.utcnow())
        end_dt = start_dt + timedelta(days=1)

        # Act
        user_activity = github_client.user_activity_during_range(
            user="alysivji", start_dt=start_dt, end_dt=end_dt
        )

        # Assert
        assert len(user_activity) >= 0
        for event in user_activity:
            assert start_dt <= parse_dt(event["created_at"]) <= end_dt

    @pytest.mark.vcr()
    def test_all_user_repos(self, github_client):
        all_repos = github_client.all_user_repos("alysivji")

        assert len(all_repos) >= 50

    @pytest.mark.vcr()
    def test_user_details(self, github_client):
        details = github_client.user_details()

        assert details["login"] == "alysivji"


class TestAsyncGitHubClient:
    @pytest.mark.vcr()
    @pytest.mark.freeze_time("2021-08-28")
    def test_get_activity_for_users(self, async_github_client):
        # Arrange -- create 1 real github user, 1 fake user
        usernames = ["alysivji", "albcae324sdf"]

        # Arrange -- time period we are searching for
        start_dt, end_dt = generate_range_utc_now_minus(timedelta(days=1))
        result = async_github_client.get_activity_for_users(usernames, start_dt, end_dt)

        # Assert -- data was pulled for valid users
        assert result.keys() == set(["alysivji"])

        # Assert -- user has github info
        assert len(result["alysivji"]) > 0


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


@pytest.mark.unit
class TestApiNav:
    def test_parsing_header_links(self):
        # Arrange
        link_header = (
            '<https://api.github.com/user/4369343/events/public?page=3>; rel="next", '
            '<https://api.github.com/user/4369343/events/public?page=10>; rel="last", '
            '<https://api.github.com/user/4369343/events/public?page=1>; rel="prev", '
            '<https://api.github.com/user/4369343/events/public?page=1>; rel="first"'
        )

        # Act
        links = ApiNav.parse_github_links(link_header)

        # Assert
        expected = ApiNav(
            first_link="https://api.github.com/user/4369343/events/public?page=1",
            prev_link="https://api.github.com/user/4369343/events/public?page=1",
            next_link="https://api.github.com/user/4369343/events/public?page=3",
            last_link="https://api.github.com/user/4369343/events/public?page=10",
        )
        assert links == expected

    def test_parsing_header_links_empty(self):
        # Arrange
        link_header = ""

        # Act
        # Assert
        with pytest.raises(ValueError):
            ApiNav.parse_github_links(link_header)
