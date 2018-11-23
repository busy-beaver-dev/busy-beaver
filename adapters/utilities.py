from typing import NamedTuple, Tuple
import urllib


class APINav(NamedTuple):
    """API Navigation Panel"""

    first_link: str = None
    last_link: str = None
    next_link: str = None
    prev_link: str = None


class GitHubLink(NamedTuple):
    type_: str
    url: str


def create_github_navigation_panel(links):
    first_link, last_link, next_link, prev_link = [None, None, None, None]
    for link in _all_links(links):
        if link.type_ == "first":
            first_link = link.url
        elif link.type_ == "last":
            last_link = link.url
        elif link.type_ == "next":
            next_link = link.url
        elif link.type_ == "prev":
            prev_link = link.url
        else:
            ValueError
    return APINav(
        first_link=first_link,
        last_link=last_link,
        next_link=next_link,
        prev_link=prev_link,
    )


def _all_links(links: str) -> Tuple[str, str]:
    for link in links.split(", "):
        dirty_url, dirty_type = link.split("; ")
        cleaned_url = dirty_url.split("<")[1][:-1]
        cleaned_type = dirty_type.split('="')[1][:-1]
        yield GitHubLink(cleaned_type, cleaned_url)


def page_from_url(url) -> int:
    url_details = urllib.parse.urlparse(url)
    query_string = url_details.query
    params = urllib.parse.parse_qs(query_string)
    return int(params['page'][0])
