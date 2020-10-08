from json import JSONDecodeError
import logging
from typing import Any, Dict, List, NamedTuple, Union

import requests

logger = logging.getLogger(__name__)
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "BusyBeaver",
}


class Response(NamedTuple):
    status_code: int
    headers: Dict[str, str]
    json: Union[List[Dict[str, Any]], Dict[str, Any]] = None


class RequestsClient:
    """Wrapper around requests to simplify interaction with JSON REST APIs"""

    def __init__(self, headers: dict = None, raise_for_status: bool = True):
        if headers is None:
            headers = {}

        self.session = requests.Session()
        self.headers = DEFAULT_HEADERS | headers
        self.raise_for_status = raise_for_status

    def __repr__(self):  # pragma: no cover
        return "RequestsClient"

    def get(self, url: str, **kwargs) -> Response:
        return self._request("get", url, **kwargs)

    def head(self, url: str, **kwargs) -> Response:
        return self._request("head", url, **kwargs)

    def post(self, url: str, **kwargs) -> Response:
        return self._request("post", url, **kwargs)

    def _request(self, method: str, url: str, **kwargs) -> Response:
        headers_to_add = kwargs.pop("headers", {})
        req_headers = self.headers | headers_to_add
        r = self.session.request(method, url, headers=req_headers, **kwargs)
        if self.raise_for_status:
            r.raise_for_status()

        try:
            resp = Response(status_code=r.status_code, headers=r.headers, json=r.json())
        except JSONDecodeError:
            resp = Response(status_code=r.status_code, headers=r.headers)
        return resp
