from datetime import datetime
from typing import Dict, List

from dateutil.parser import parse as date_parse

from ..exceptions import UnexpectedStatusCode
from .requests_client import RequestsClient, Response
from .utilities import (
    create_github_navigation_panel,
    filter_items_before,
    page_from_url,
)

BASE_URL = "https://api.github.com"
USER_AGENT = "BusyBeaver"


class GitHubAdapter:
    def __init__(self, oauth_token: str):
        self.client = RequestsClient()
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {oauth_token}",
        }
        self.params = {"per_page": 30}
        self.nav = None

    def __repr__(self):
        return "GitHubAdapter"

    def sitemap(self):
        url = BASE_URL + "/"
        return self.__get(url)

    def all_user_repos(self, user: str, *, max_pages: int = 10) -> List[Dict]:
        url = BASE_URL + f"/users/{user}/repos"
        all_repos = self._get_all_items(url, max_pages=max_pages)
        return all_repos

    def all_user_stars(self, user: str, *, max_pages: int = 10) -> List[Dict]:
        url = BASE_URL + f"/users/{user}/starred"
        all_stars = self._get_all_items(url, max_pages=max_pages)
        return all_stars

    def user_activity_after(self, user: str, timestamp: datetime) -> List[Dict]:
        url = BASE_URL + f"/users/{user}/events/public"
        user_events = self._get_items_after_timestamp(url, timestamp=timestamp)
        return user_events

    def _get_all_items(self, url: str, *, max_pages: int = 5) -> List[Dict]:
        resp = self.__head(url)
        headers = resp.headers

        try:
            nav = create_github_navigation_panel(headers["Link"])
            last_page = page_from_url(nav.last_link)
        except KeyError:
            last_page = 1

        all_items = []
        for page_num in range(1, min(last_page, max_pages) + 1):
            combined_params = self.params.copy()
            combined_params.update({"page": page_num})
            resp = self.__get(url, params=combined_params)
            all_items.extend(resp.json)

        return all_items

    def _get_items_after_timestamp(self, url: str, *, timestamp: datetime) -> List[Dict]:
        """Keep fetching until we have captured the timestamp or are on the last page"""
        all_items = []
        page_num = 1

        while True:
            combined_params = self.params.copy()
            combined_params.update({"page": page_num})
            resp = self.__get(url, params=combined_params)
            all_items.extend(resp.json)

            single_page_of_activity = "Link" not in resp.headers
            if single_page_of_activity:
                break

            nav = create_github_navigation_panel(resp.headers["Link"])
            last_page = page_from_url(nav.last_link)
            min_batch_timestamp = date_parse(resp.json[-1]["created_at"])
            keep_fetching = timestamp <= min_batch_timestamp and page_num < last_page
            if not keep_fetching:
                break

            page_num = page_num + 1

        filtered_items = filter_items_before(timestamp=timestamp, items=all_items)
        return filtered_items

    def __get(self, url: str, **kwargs) -> Response:
        resp = self.client.get(url, headers=self.headers, **kwargs)
        if resp.status_code != 200:
            raise UnexpectedStatusCode
        return resp

    def __head(self, url: str, **kwargs) -> Response:
        resp = self.client.head(url, headers=self.headers, **kwargs)
        if resp.status_code != 200:
            raise UnexpectedStatusCode
        return resp
