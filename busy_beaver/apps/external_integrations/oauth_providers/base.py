from typing import NamedTuple


class OAuthError(Exception):
    pass


class ExternalOAuthDetails(NamedTuple):
    url: str
    state: str


class OAuthFlowInterface:
    """Defining a common API to add consistency to software design process"""

    def __init__(self, client_id, client_secret):
        return NotImplementedError

    def generate_authentication_tuple(self) -> ExternalOAuthDetails:
        """Creates a (URL, state) tuple used to authenticate users"""
        return NotImplementedError

    def process_callback(self, authorization_response_url, state):
        """Handles callback made by authentication service servers to verify users"""
        return NotImplementedError
