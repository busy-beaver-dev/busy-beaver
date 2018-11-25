from json import JSONDecodeError
import logging
from typing import Any, Dict, List, NamedTuple, Union

import requests

logger = logging.getLogger(__name__)


class Response(NamedTuple):
    status_code: int
    headers: Dict[str, str]
    json: Union[List[Dict[str, Any]], Dict[str, Any]] = None


class RequestsClient:
    def __init__(self):
        s = requests.Session()
        self.session = s

    def __repr__(self):
        return "RequestsClient"

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        r = self.session.request(method, url, **kwargs)
        try:
            resp = Response(status_code=r.status_code, headers=r.headers, json=r.json())
        except JSONDecodeError:
            resp = Response(status_code=r.status_code, headers=r.headers)
        return resp

    def get(self, url: str, **kwargs) -> Response:
        return self._request("get", url, **kwargs)

    def head(self, url: str, **kwargs) -> Response:
        return self._request("head", url, **kwargs)
