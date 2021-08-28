"""Third-party integrations

This module contains logic to configure third-party
integrations. The integrations in this module are
global across the application.

Variables are assigned Singleton instances of each
integration.
"""

from .common.wrappers import (
    AsyncGitHubClient,
    GitHubClient,
    MeetupClient,
    S3Client,
    SlackClient,
)
from .config import (
    DIGITALOCEAN_SPACES_KEY,
    DIGITALOCEAN_SPACES_SECRET,
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_OAUTH_TOKEN,
    MEETUP_API_KEY,
    SLACK_CLIENT_ID,
    SLACK_CLIENT_SECRET,
    SLACK_TOKEN,
)
from busy_beaver.apps.github_integration.oauth.oauth_flow import GitHubOAuthFlow
from busy_beaver.apps.slack_integration.oauth.oauth_flow import (
    SlackInstallationOAuthFlow,
    SlackSignInOAuthFlow,
)

chipy_slack = SlackClient(SLACK_TOKEN)  # Default Workspace -- this is being phased out
github = GitHubClient(GITHUB_OAUTH_TOKEN)
github_async = AsyncGitHubClient(GITHUB_OAUTH_TOKEN)
meetup = MeetupClient(MEETUP_API_KEY)

slack_install_oauth = SlackInstallationOAuthFlow(SLACK_CLIENT_ID, SLACK_CLIENT_SECRET)
slack_signin_oauth = SlackSignInOAuthFlow(SLACK_CLIENT_ID, SLACK_CLIENT_SECRET)
github_oauth = GitHubOAuthFlow(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)

s3 = S3Client(DIGITALOCEAN_SPACES_KEY, DIGITALOCEAN_SPACES_SECRET)
