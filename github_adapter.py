from http import HTTPStatus
import logging
import os

import requests

BASE_URL = "https://api.github.com"
USER_AGENT = "BusyBeaver"

logger = logging.getLogger(__name__)


class GitHubAdapter:
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

    def _get_request(self, url):
        resp = self.session.get(url)
        if resp.status_code != HTTPStatus.OK:
            logger.error(f"Recieved {resp.status_code}")
            resp.raise_for_status()
        return resp

    def sitemap(self):
        url = BASE_URL + "/"
        return self._get_request(url)

    def public_events(self):
        url = BASE_URL + "/events"
        return self._get_request(url)

    def events(self, user):
        url = BASE_URL + f"/users/{user}/events/public"
        return self._get_request(url)

    def __repr__(self):
        return "GitHubAdapter_sync"


if __name__ == "__main__":
    oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")
    client = GitHubAdapter(oauth_token)
