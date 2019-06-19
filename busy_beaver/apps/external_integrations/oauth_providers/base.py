from typing import NamedTuple


class OAuthError(Exception):
    status_code = 403

    def __init__(self, error):
        super().__init__()
        self.message = error


class ExternalOAuthDetails(NamedTuple):
    url: str
    state: str


class OAuthFlowInterface:
    """Defining a common API to add consistency to software design process"""

    def __init__(self, client_id, client_secret):
        return NotImplementedError  # pragma: no cover

    def generate_authentication_tuple(self) -> ExternalOAuthDetails:
        """Creates a (URL, state) tuple used to authenticate users"""
        return NotImplementedError  # pragma: no cover

    def process_callback(self, authorization_response_url, state):
        """Handles callback made by authentication service servers to verify users"""
        return NotImplementedError  # pragma: no cover
