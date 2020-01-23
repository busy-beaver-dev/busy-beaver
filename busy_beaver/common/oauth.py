"""OAuth Integrations

This module ontains logic for integration with third-party APIs.
We provide a nice wrapper around `requests-oauthlib` to
simplify the OAuth process for the user..
"""

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
    def __init__(self, client_id, client_secret):  # pragma: no cover
        pass

    @abc.abstractmethod
    def generate_authentication_tuple(self) -> ExternalOAuthDetails:  # pragma: no cover
        """Creates a (URL, state) tuple used to authenticate users"""
        pass

    @abc.abstractmethod
    def process_callback(self, authorization_response_url, state):  # pragma: no cover
        """Handles callback made by authentication service servers to verify users"""
        pass
