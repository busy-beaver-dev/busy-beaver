from http import HTTPStatus
import logging
import os
from typing import Any, Dict, List, NamedTuple, Union

import requests

BASE_URL = "https://api.github.com"
USER_AGENT = "BusyBeaver"
'<https://api.github.com/user/4369343/events/public?page=2>; rel="next"'

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
        # extracted_url = link.split('<')[1].split('>')[0]
        # clearned_url = dirty_url.split("<")[1][:-1]

        # query_string = url_details.query
        # params = urllib.parse.parse_qs(query_string)
        # return int(params['page'][0])

    # def _parse_link_header(links: str) -> links:

    #     for link in links.split(", "):
    #         link_type = link.split("; rel=")

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
        return self._get_request(url)


if __name__ == "__main__":
    oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")
    client = GitHubAdapter(oauth_token)
    sitemap = client.sitemap()
