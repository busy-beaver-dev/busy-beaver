from http import HTTPStatus
import logging
import os
from typing import Any, Dict, List, NamedTuple, Union

import requests

# from .utilities import parse_header_linksa

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

    def __repr__(self):
        return "GitHubAdapter_sync"

    ################
    # Helper Methods
    ################
    def _get_request(self, url: str) -> Response:
        resp = self.session.get(url)
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

    def user_events(self, user: str) -> Response:
        url = BASE_URL + f"/users/{user}/events/public"
        headers, body = self._get_request(url)


if __name__ == "__main__":
    oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")
    client = GitHubAdapterSync(oauth_token)

    my_events = client.user_events("alysivji")
    headers = my_events.headers
    body = my_events.json
