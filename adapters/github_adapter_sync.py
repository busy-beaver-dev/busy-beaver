from datetime import datetime
from http import HTTPStatus
import logging
import os
from typing import Any, Dict, List, NamedTuple, Union

from dateutil.parser import parse as date_parse
import requests

from adapters.utilities import (
    create_github_navigation_panel,
    filter_items_before,
    page_from_url,
)

BASE_URL = "https://api.github.com"
USER_AGENT = "BusyBeaver"

logger = logging.getLogger(__name__)


class Response(NamedTuple):
    headers: Dict[str, str]
    json: Union[List[Dict[str, Any]], Dict[str, Any]]


class GitHubAdapterSync:
    """Synchronous version using requests"""

    def __init__(self, oauth_token):
        s = requests.Session()
        s.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {oauth_token}",
            "Content-Type": "application/json",
            "User-Agent": f"{USER_AGENT}_sync",
        }
        self.session = s
        self.params = {"per_page": 30}
        self.nav = None

    def __repr__(self):
        return "GitHubAdapter_sync"

    ################
    # Helper Methods
    ################
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        return self.session.request(method, url, **kwargs)

    def _head(self, url: str) -> Response:
        resp = self._request("head", url)
        if resp.status_code != HTTPStatus.OK:
            logger.error(f"Recieved {resp.status_code}")
            resp.raise_for_status()
        return Response(headers=resp.headers, json=None)

    def _get(self, url: str, params: dict) -> Response:
        combined_params = self.params.copy()
        combined_params.update(params)
        resp = self._request("get", url, params=combined_params)
        if resp.status_code != HTTPStatus.OK:
            logger.error(f"Recieved {resp.status_code}")
            resp.raise_for_status()
        return Response(headers=resp.headers, json=resp.json())

    def _get_items_after_timestamp(self, url: str, *, timestamp: datetime) -> List[Dict]:
        """Keep fetching until we have captured the timestamp or are on the last page"""
        all_items = []
        page_num = 1
        while True:
            headers, resp_json = self._get(url, params={"page": page_num})
            all_items.extend(resp_json)
            nav = create_github_navigation_panel(headers["Link"])
            last_page = page_from_url(nav.last_link)

            min_batch_timestamp = date_parse(resp_json[-1]["created_at"])
            keep_fetching = timestamp <= min_batch_timestamp and page_num < last_page
            if not keep_fetching:
                break

            page_num = page_num + 1

        filtered_items = filter_items_before(timestamp=timestamp, items=all_items)
        return filtered_items

    def _get_all_items(self, url: str, *, max_pages: int = 5) -> List[Dict]:
        resp = self._head(url)
        headers = resp.headers
        nav = create_github_navigation_panel(headers["Link"])
        last_page = page_from_url(nav.last_link)

        all_items = []
        for page_num in range(1, min(last_page, max_pages) + 1):
            headers, resp_json = self._get(url, params={"page": page_num})
            all_items.extend(resp_json)

        return all_items

    ############
    # Public API
    ############
    def sitemap(self):
        url = BASE_URL + "/"
        return self._get(url)

    def all_public_events(self) -> Response:
        # refactor
        url = BASE_URL + "/events"
        return self._get(url)

    def all_user_repos(self, user: str, *, max_pages=10):
        url = BASE_URL + f"/users/{user}/repos"
        all_repos = self._get_all_items(url, max_pages=max_pages)
        return all_repos

    def all_user_stars(self, user: str, *, max_pages=10):
        url = BASE_URL + f"/users/{user}/starred"
        all_stars = self._get_all_items(url, max_pages=max_pages)
        return all_stars

    def user_activity_after(self, user: str, timestamp) -> List[Dict]:
        url = BASE_URL + f"/users/{user}/events/public"
        user_events = self._get_items_after_timestamp(url, timestamp=timestamp)
        return user_events


if __name__ == "__main__":
    oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")
    client = GitHubAdapterSync(oauth_token)

    from datetime import timedelta
    from adapters.utilities import subtract_timedelta

    boundary_dt = subtract_timedelta(timedelta(days=1))
