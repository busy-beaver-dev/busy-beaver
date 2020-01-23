import abc
from typing import NamedTuple


class OAuthError(Exception):
    status_code = 403

    def __init__(self, error):
        super().__init__()
        self.message = error


class ExternalOAuthDetails(NamedTuple):
    url: str
    state: str


class OAuthFlow(abc.ABC):
    """Defining a common API to add consistency to software design process"""

    @abc.abstractmethod
    def __init__(self, client_id, client_secret):  # noqa
        pass

    @abc.abstractmethod
    def generate_authentication_tuple(self) -> ExternalOAuthDetails:  # noqa
        """Creates a (URL, state) tuple used to authenticate users"""
        pass

    @abc.abstractmethod
    def process_callback(self, authorization_response_url, state):  # noqa
        """Handles callback made by authentication service servers to verify users"""
        pass
