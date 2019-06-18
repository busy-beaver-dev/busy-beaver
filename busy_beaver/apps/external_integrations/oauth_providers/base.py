from typing import NamedTuple


class OAuthError(Exception):
    pass


class ExternalOAuthDetails(NamedTuple):
    url: str
    state: str
