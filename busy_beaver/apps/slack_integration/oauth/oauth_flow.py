import logging
from typing import NamedTuple
from urllib.parse import parse_qs, urlparse

from oauthlib.common import urldecode
import requests
from requests_oauthlib import OAuth2Session

from busy_beaver.common.oauth import ExternalOAuthDetails, OAuthError, OAuthFlow
from busy_beaver.config import BASE_URL

logger = logging.getLogger(__name__)


####################
# Slack Installation
####################
class SlackOAuthInfo(NamedTuple):
    authorizing_user_id: str
    bot_access_token: str
    bot_user_id: str
    scope: str
    workspace_id: str
    workspace_name: str
    auth_response: dict


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


class SlackInstallationOAuthFlow(OAuthFlow):
    # TODO update to v2/oauth/authorize and remove hook (write up direct token exchange)
    AUTHORIZATION_BASE_URL = "https://slack.com/oauth/authorize"
    TOKEN_URL = "https://slack.com/api/oauth.v2.access"
    SCOPES = [  # https://api.slack.com/scopes
        "app_mentions:read",
        "channels:history",
        "channels:join",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "reactions:read",
        "reactions:write",
        "team:read",
        "usergroups:read",
        "users.profile:read",
        "users:read",
        "users:write",
    ]

    @staticmethod
    def _generate_redirect_uri():
        return f"{BASE_URL}/slack/installation-callback"

    def __init__(self, client_id, client_secret):
        self.redirect_uri = self._generate_redirect_uri()
        self.session = OAuth2Session(
            client_id, scope=self.SCOPES, redirect_uri=self.redirect_uri
        )
        self.state_to_auth_response = hook = StateToOAuthResponse()
        self.session.register_compliance_hook("access_token_response", hook)
        self.client_secret = client_secret

    def generate_authentication_tuple(self) -> ExternalOAuthDetails:  # pragma: no cover
        # TODO have this on the installation page
        raise NotImplementedError

    def process_callback(self, authorization_response_url) -> SlackOAuthInfo:
        """Slack OAuth for workspace installation adds params to response

        Code is a unique identifer; use it as a unique identifer
        when we are loading additional items whenhooking into the response

        Additional Resources
            - https://api.slack.com/methods/oauth.v2.access
        """
        self._fetch_token(authorization_response_url)
        code = parse_qs(urlparse(authorization_response_url).query)["code"][0]
        oauth_response = self._parse_json_response(code)
        return SlackOAuthInfo(**oauth_response)

    def _fetch_token(self, authorization_response_url):
        workspace_credentials = self.session.fetch_token(
            self.TOKEN_URL,
            authorization_response=authorization_response_url,
            client_secret=self.client_secret,
            scope=None,
        )
        return workspace_credentials["access_token"]

    def _parse_json_response(self, code):
        oauth_json = self.state_to_auth_response.mapping.pop(code)

        # TODO do this with marshmallow
        output = {}
        output["scope"] = oauth_json["scope"]
        output["authorizing_user_id"] = oauth_json["authed_user"]["id"]
        output["workspace_id"] = oauth_json["team"]["id"]
        output["workspace_name"] = oauth_json["team"]["name"]
        output["bot_user_id"] = oauth_json["bot_user_id"]
        output["bot_access_token"] = oauth_json["access_token"]
        output["auth_response"] = oauth_json
        return output


###############
# Slack Sign-in
###############
class SlackSignInDetails(NamedTuple):
    slack_id: str
    workspace_id: str
    scope: str
    access_token: str
    token_type: str


class SlackSignInOAuthFlow(OAuthFlow):
    """Sign-in with Slack

    Docs:
     - https://api.slack.com/docs/sign-in-with-slack
    """

    AUTHORIZATION_BASE_URL = "https://slack.com/oauth/v2/authorize"
    TOKEN_URL = "https://slack.com/api/oauth.v2.access"
    SCOPES = ["identity.basic"]

    @staticmethod
    def _generate_redirect_uri():
        return f"{BASE_URL}/slack/sign-in-callback"

    def __init__(self, client_id, client_secret):
        self.redirect_uri = self._generate_redirect_uri()
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = OAuth2Session(
            client_id, scope=self.SCOPES, redirect_uri=self.redirect_uri
        )

    def generate_authentication_tuple(self) -> ExternalOAuthDetails:
        self.url = self.AUTHORIZATION_BASE_URL
        authorization_url, state = self.session.authorization_url(self.url)
        authorization_url = authorization_url.replace("scope=", "user_scope=")
        return ExternalOAuthDetails(url=authorization_url, state=state)

    def process_callback(self, authorization_response_url) -> SlackSignInDetails:
        user_credentials = self._fetch_token(authorization_response_url)
        return SlackSignInDetails(
            slack_id=user_credentials["authed_user"]["id"],
            workspace_id=user_credentials["team"]["id"],
            scope=user_credentials["authed_user"]["scope"],
            access_token=user_credentials["authed_user"]["access_token"],
            token_type=user_credentials["authed_user"]["token_type"],
        )

    def _fetch_token(self, authorization_response_url):
        code = parse_qs(urlparse(authorization_response_url).query)["code"][0]
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        resp = requests.get(self.TOKEN_URL, params=params)
        if resp.status_code != 200:
            logger.error("Slack Sign-in OAuth -- Bad Response")
            raise OAuthError("Server error. Please try again in a few minutes.")

        data = resp.json()
        if not data["ok"]:
            error = data["error"]
            logger.error("Slack Sign-in OAuth -- Flow Failed", extra={"error": error})
            raise OAuthError(error)
        return data
