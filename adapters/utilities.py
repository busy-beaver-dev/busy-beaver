from typing import NamedTuple
import urllib


class GitHubLink(NamedTuple):
    type_: str
    url: str


def header_links(links_header: str):
    for link in links_header.split(", "):
        dirty_url, dirty_type = link.split("; ")
        cleaned_url = dirty_url.split("<")[1][:-1]
        cleaned_type = dirty_type.split('="')[1][:-1]
        yield GitHubLink(type_=cleaned_type, url=cleaned_url)
