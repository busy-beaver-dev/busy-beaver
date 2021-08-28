import asyncio
from datetime import datetime
from typing import Dict, List, NamedTuple, Tuple
import urllib

from dateutil.parser import parse as date_parse
import httpx

from .requests_client import RequestsClient, Response
from busy_beaver.exceptions import UnexpectedStatusCode

BASE_URL = "https://api.github.com"


class GitHubClient:
    def __init__(self, oauth_token: str):
        default_headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {oauth_token}",
        }
        self.client = RequestsClient(headers=default_headers)
        self.params = {"per_page": 30}
        self.nav = None

    def __repr__(self):  # pragma: no cover
        return "GitHubAdapter"

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

    def user_activity_during_range(
        self, user: str, start_dt: datetime, end_dt: datetime
    ) -> List[Dict]:
        url = BASE_URL + f"/users/{user}/events/public"
        user_events = self._get_items_after_timestamp(url, timestamp=start_dt)

        idx = 0
        for idx, event in enumerate(user_events):
            dt = date_parse(event["created_at"])
            if dt <= end_dt:
                break
        return user_events[idx:]

    def user_details(self):
        url = f"{BASE_URL}/user"
        return self.__get(url).json

    def _get_all_items(self, url, *, max_pages=5) -> List[Dict]:
        resp = self.__head(url)
        headers = resp.headers

        try:
            nav = ApiNav.parse_github_links(headers["Link"])
            last_page = page_from_url(nav.last_link)
        except KeyError:
            last_page = 1

        all_items = []
        for page_num in range(1, min(last_page, max_pages) + 1):
            combined_params = self.params | {"page": page_num}
            resp = self.__get(url, params=combined_params)
            all_items.extend(resp.json)

        return all_items

    def _get_items_after_timestamp(self, url, *, timestamp) -> List[Dict]:
        """Keep fetching until we have captured the timestamp or are on the last page"""
        all_items = []
        page_num = 1

        while True:
            combined_params = self.params | {"page": page_num}
            resp = self.__get(url, params=combined_params)
            all_items.extend(resp.json)

            single_page_of_activity = "Link" not in resp.headers
            if single_page_of_activity:
                break

            nav = ApiNav.parse_github_links(resp.headers["Link"])
            last_page = page_from_url(nav.last_link)
            min_batch_timestamp = date_parse(resp.json[-1]["created_at"])
            keep_fetching = timestamp <= min_batch_timestamp and page_num < last_page
            if not keep_fetching:
                break

            page_num = page_num + 1

        filtered_items = filter_items_before(timestamp=timestamp, items=all_items)
        return filtered_items

    def __get(self, url, **kwargs) -> Response:
        resp = self.client.get(url, **kwargs)
        if resp.status_code != 200:
            raise UnexpectedStatusCode
        return resp

    def __head(self, url, **kwargs) -> Response:
        resp = self.client.head(url, **kwargs)
        if resp.status_code != 200:
            raise UnexpectedStatusCode
        return resp


def filter_items_before(timestamp: datetime, items: list):
    """If event happened after timestamp, keep it"""
    keep_item = [date_parse(item["created_at"]) > timestamp for item in items]

    filtered_items = items[:]
    items_to_pop = len(items) - sum(keep_item)
    for _ in range(items_to_pop):
        filtered_items.pop()

    return filtered_items


def page_from_url(url: str) -> int:
    url_details = urllib.parse.urlparse(url)
    query_string = url_details.query
    params = urllib.parse.parse_qs(query_string)
    return int(params["page"][0])


class ApiNav(NamedTuple):
    first_link: str = None
    last_link: str = None
    next_link: str = None
    prev_link: str = None

    @classmethod
    def parse_github_links(cls, links):
        def all_links(links: str) -> Tuple[str, str]:
            for link in links.split(", "):
                dirty_url, dirty_type = link.split("; ")
                cleaned_url = dirty_url.split("<")[1][:-1]
                cleaned_type = dirty_type.split('="')[1][:-1]
                yield GitHubLink(cleaned_type, cleaned_url)

        links = {link.type_: link.url for link in all_links(links)}
        return cls(
            first_link=links.get("first"),
            last_link=links.get("last"),
            next_link=links.get("next"),
            prev_link=links.get("prev"),
        )


class GitHubLink(NamedTuple):
    type_: str
    url: str


class AsyncGitHubClient:
    def __init__(self, oauth_token: str):
        self.headers = {  # TODO: use this
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {oauth_token}",
        }
        self.params = {"per_page": 30}
        self.nav = None

    def __repr__(self):  # pragma: no cover
        return "AsyncGitHubAdapter"

    def get_activity_for_users(
        self,
        users: List[str],
        start_dt: datetime,
        end_dt: datetime,
    ) -> Dict[str, list]:
        """
        Entry point for clients;
        kicks off fetching user activity from GitHub API using asyncio

        Is there a cleaner way to do this?
        """
        task = self._get_activity_for_users(users, start_dt, end_dt)
        return asyncio.run(task)

    async def _get_activity_for_users(
        self,
        users: List[str],
        start_dt: datetime,
        end_dt: datetime,  # comma separated list
    ) -> Dict[str, list]:
        client = httpx.AsyncClient()
        # client = httpx.AsyncClient(headers=self.headers, params=self.params)
        async with client:
            tasks = []
            for user in users:
                task = self._user_activity_during_range(client, user, start_dt, end_dt)
                tasks.append(task)

            user_activity_results = await asyncio.gather(*tasks, return_exceptions=True)

            user_activity_dict = {}
            for result in user_activity_results:
                if isinstance(result, Exception):
                    # TODO how to deal with exceptions?
                    continue
                user, events = result
                user_activity_dict[user] = events

        return user_activity_dict

    async def _user_activity_during_range(
        self,
        client: httpx.AsyncClient,
        user: str,
        start_dt: datetime,
        end_dt: datetime,
    ) -> List[Dict]:
        url = BASE_URL + f"/users/{user}/events/public"
        user_events = await self._get_items_after_timestamp(
            client,
            url,
            timestamp=start_dt,
        )

        idx = 0
        for idx, event in enumerate(user_events):
            dt = date_parse(event["created_at"])
            if dt <= end_dt:
                break
        return (user, user_events[idx:])

    async def _get_items_after_timestamp(self, client, url, *, timestamp) -> List[Dict]:
        """Keep fetching until we have captured the timestamp or are on the last page"""
        all_items = []
        page_num = 1

        while True:
            combined_params = self.params | {"page": page_num}
            resp = await client.get(url, params=combined_params)
            if resp.status_code != 200:
                raise UnexpectedStatusCode
            all_items.extend(resp.json())

            single_page_of_activity = "Link" not in resp.headers
            if single_page_of_activity:
                break

            nav = ApiNav.parse_github_links(resp.headers["Link"])
            last_page = page_from_url(nav.last_link)
            min_batch_timestamp = date_parse(resp.json()[-1]["created_at"])
            keep_fetching = timestamp <= min_batch_timestamp and page_num < last_page
            if not keep_fetching:
                break

            page_num = page_num + 1

        filtered_items = filter_items_before(timestamp=timestamp, items=all_items)
        return filtered_items
