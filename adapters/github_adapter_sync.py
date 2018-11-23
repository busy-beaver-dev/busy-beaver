from datetime import datetime, timedelta
from http import HTTPStatus
import logging
import os
from typing import Any, Dict, List, NamedTuple, Union

from dateutil.parser import parse as dateutil_parse
import pytz
import requests

from adapters.utilities import create_github_navigation_panel, page_from_url

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
        self.nav = None

    def __repr__(self):
        return "GitHubAdapter_sync"

    ################
    # Helper Methods
    ################
    def _get_request(self, url: str, params: dict) -> Response:
        resp = self.session.get(url, params=params)
        if resp.status_code != HTTPStatus.OK:
            logger.error(f"Recieved {resp.status_code}")
            resp.raise_for_status()
        return Response(headers=resp.headers, json=resp.json())

    ############
    # Public API
    ############
    def sitemap(self):
        url = BASE_URL + "/"
        return self._get_request(url)

    def all_public_events(self) -> Response:
        url = BASE_URL + "/events"
        return self._get_request(url)

    def latest_user_events(self, user: str, period: timedelta) -> Response:
        url = BASE_URL + f"/users/{user}/events/public"

        all_events = []
        page_num = 1

        now = pytz.utc.localize(datetime.utcnow())
        boundary_dt = now + period
        while True:
            headers, resp_json = self._get_request(url, {"page": page_num})
            all_events.extend(resp_json)
            nav = create_github_navigation_panel(headers["Link"])

            earliest_event_in_batch = dateutil_parse(resp_json[-1]["created_at"])
            fetch_next_page = (
                page_num < page_from_url(nav.last_link)
                and boundary_dt <= earliest_event_in_batch
            )
            if not fetch_next_page:
                break

            page_num = page_num + 1

        while True:
            if dateutil_parse(all_events[-1]["created_at"]) >= boundary_dt:
                break
            all_events.pop()

        return all_events


if __name__ == "__main__":
    oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")
    client = GitHubAdapterSync(oauth_token)

    my_events = client.latest_user_events("alysivji", period=timedelta(days=-1))
