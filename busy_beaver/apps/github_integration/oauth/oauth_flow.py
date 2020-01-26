from typing import NamedTuple

from requests_oauthlib import OAuth2Session
from busy_beaver.adapters import GitHubClient

from busy_beaver.common.oauth import OAuthFlow, ExternalOAuthDetails


class GitHubOAuthInfo(NamedTuple):
    access_token: str
    github_id: str
    github_username: str


class GitHubOAuthFlow(OAuthFlow):
    AUTHORIZATION_BASE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"

    def __init__(self, client_id, client_secret):
        self.session = OAuth2Session(client_id)
        self.client_secret = client_secret

    def generate_authentication_tuple(self) -> ExternalOAuthDetails:
        url = self.AUTHORIZATION_BASE_URL
        authorization_url, state = self.session.authorization_url(url)
        return ExternalOAuthDetails(url=authorization_url, state=state)

    def process_callback(self, authorization_response_url, state) -> GitHubOAuthInfo:
        access_token = self._fetch_token(authorization_response_url, state)
        github_id, github_username = self._fetch_github_account_details(access_token)
        return GitHubOAuthInfo(access_token, github_id, github_username)

    def _fetch_token(self, authorization_response_url, state):
        user_credentials = self.session.fetch_token(
            self.TOKEN_URL,
            authorization_response=authorization_response_url,
            client_secret=self.client_secret,
            state=state,
        )
        return user_credentials["access_token"]

    @staticmethod
    def _fetch_github_account_details(access_token):
        github = GitHubClient(access_token)
        user_details = github.user_details()

        github_id = user_details["id"]
        github_username = user_details["login"]
        return (github_id, github_username)
