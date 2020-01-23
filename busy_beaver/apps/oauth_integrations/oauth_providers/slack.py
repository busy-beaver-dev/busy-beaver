from typing import NamedTuple
from urllib.parse import parse_qs, urlparse

from oauthlib.common import urldecode
from requests_oauthlib import OAuth2Session

from .base import ExternalOAuthDetails


class SlackOAuthInfo(NamedTuple):
    access_token: str
    authorizing_user_id: str
    bot_access_token: str
    bot_user_id: str
    scope: str
    workspace_id: str
    workspace_name: str


class StateToOAuthResponse:
    """Hook that grabs response information during token exchange.

    When the code is exchanged for a token in the OAuth2 workflow,
    Slack also sends bot tokens and information about the workspace.

    Use a hook to capture items in a stateful dictionary;
    the code parameter is the key for this dictionary;
    used as a state param.

    https://requests-oauthlib.readthedocs.io/en/latest/api.html
    """

    def __init__(self):
        self.mapping = {}

    def __call__(self, response):
        """Hook is required to be callable"""

        req_params = {k: v for k, v in urldecode(response.request.body)}
        code = req_params["code"]  # this is the unique param
        self.mapping[code] = response.json()
        return response


class SlackOAuthFlow:
    AUTHORIZATION_BASE_URL = "https://slack.com/oauth/authorize"
    TOKEN_URL = "https://slack.com/api/oauth.access"
    SCOPES = [
        "bot",  # enable bot user
        "channels:read",  # read list of channels
        "chat:write:bot",  # allow bot to write in channels
        "commands",  # enable slash commands
    ]

    def __init__(self, client_id, client_secret):
        self.session = OAuth2Session(client_id, scope=self.SCOPES)
        self.state_to_auth_response = hook = StateToOAuthResponse()
        self.session.register_compliance_hook("access_token_response", hook)
        self.client_secret = client_secret

    def generate_authentication_tuple(self) -> ExternalOAuthDetails:
        raise NotImplementedError  # pragma: no cover

    def process_callback(self, authorization_response_url, state) -> SlackOAuthInfo:
        """Slack OAuth for workspace installation adds params to response

        Code is a unique identifer; use it as a unique identifer
        when we are loading additional items whenhooking into the response

        Additional Resources
            - https://api.slack.com/methods/oauth.access
        """
        self._fetch_token(authorization_response_url, state)
        code = parse_qs(urlparse(authorization_response_url).query)["code"][0]
        oauth_response = self._parse_json_response(code)
        return SlackOAuthInfo(**oauth_response)

    def _fetch_token(self, authorization_response_url, state):
        workspace_credentials = self.session.fetch_token(
            self.TOKEN_URL,
            authorization_response=authorization_response_url,
            client_secret=self.client_secret,
            state=state,
            scope=None,
        )
        return workspace_credentials["access_token"]

    def _parse_json_response(self, code):
        oauth_json = self.state_to_auth_response.mapping.pop(code)

        # TODO do this with marshmallow
        output = {}
        output["access_token"] = oauth_json["access_token"]
        output["scope"] = oauth_json["scope"]
        output["authorizing_user_id"] = oauth_json["user_id"]
        output["workspace_id"] = oauth_json["team_id"]
        output["workspace_name"] = oauth_json["team_name"]
        output["bot_user_id"] = oauth_json["bot"]["bot_user_id"]
        output["bot_access_token"] = oauth_json["bot"]["bot_access_token"]
        return output
