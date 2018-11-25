import requests

USER_AGENT = "BusyBeaver"


class RequestsClient:
    def __init__(self, oauth_token: str):
        s = requests.Session()
        s.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {oauth_token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }
        self.session = s

    def __repr__(self):
        return "RequestsClient"

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        return self.session.request(method, url, **kwargs)
