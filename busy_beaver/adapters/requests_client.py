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

    def __init__(self, headers: dict = None):
        _headers = dict(DEFAULT_HEADERS)
        if headers is not None:
            _headers.update(headers)

        s = requests.Session()
        self.headers = _headers
        self.session = s

    def __repr__(self):
        return "RequestsClient"

    def get(self, url: str, **kwargs) -> Response:
        return self._request("get", url, **kwargs)

    def head(self, url: str, **kwargs) -> Response:
        return self._request("head", url, **kwargs)

    def _request(self, method: str, url: str, **kwargs) -> Response:
        req_headers = dict(self.headers)
        if "headers" in kwargs:
            headers_to_add = kwargs.pop("headers")
            req_headers.update(headers_to_add)

        r = self.session.request(method, url, headers=req_headers, **kwargs)
        r.raise_for_status()

        try:
            resp = Response(status_code=r.status_code, headers=r.headers, json=r.json())
        except JSONDecodeError:
            resp = Response(status_code=r.status_code, headers=r.headers)
        return resp
