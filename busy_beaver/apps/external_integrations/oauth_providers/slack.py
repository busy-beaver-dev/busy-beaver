from typing import NamedTuple

from oauthlib.common import urldecode
from requests_oauthlib import OAuth2Session

from .base import ExternalOAuthDetails, OAuthError


class SlackOAuthInfo(NamedTuple):
    access_token: str
    scope: str
    authorizing_user_id: str
    workspace_id: str
    workspace_name: str
    bot_user_id: str
    bot_access_token: str


class StateToOAuthResponse:
    """Hook that grabs response information during token exchange.

    When the code is exchanged for a token in the OAuth2 workflow,
    Slack also sends bot tokens and information about the workspace.

    Use a hook to capture items in a stateful dictionary.

    https://requests-oauthlib.readthedocs.io/en/latest/api.html
    """

    def __init__(self):
        self.mapping = {}

    def __call__(self, response):
        """Hook is required to be callable"""

        req_params = {k: v for k, v in urldecode(response.request.body)}
        state = req_params["state"]
        self.mapping[state] = response.json()
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
        url = self.AUTHORIZATION_BASE_URL
        authorization_url, state = self.session.authorization_url(url)
        return ExternalOAuthDetails(url=authorization_url, state=state)

    def process_callback(self, authorization_response_url, state) -> SlackOAuthInfo:
        """Slack OAuth for workspace installation adds params to response

        Additional Resources
            - https://api.slack.com/methods/oauth.access
        """
        self._fetch_token(authorization_response_url, state)
        oauth_response = self._parse_json_response(state)
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

    def _parse_json_response(self, state):
        try:
            oauth_json = self.state_to_auth_response.mapping.pop(state)
        except KeyError:
            raise OAuthError("state error") from None

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
