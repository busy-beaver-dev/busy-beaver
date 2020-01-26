"""Third-party integrations

This module contains logic to configure third-party
integrations. The integrations in this module are
global across the application.

Variables are assigned Singleton instances of each
integration.
"""

from .common.wrappers import GitHubClient, MeetupClient, SlackClient, TwitterClient
from .config import (
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_OAUTH_TOKEN,
    MEETUP_API_KEY,
    SLACK_CLIENT_ID,
    SLACK_CLIENT_SECRET,
    SLACK_TOKEN,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
)
from busy_beaver.apps.github_integration.oauth.oauth_flow import GitHubOAuthFlow
from busy_beaver.apps.slack_integration.oauth.oauth_flow import SlackOAuthFlow

chipy_slack = SlackClient(SLACK_TOKEN)  # Default Workspace -- this is being phased out
github = GitHubClient(GITHUB_OAUTH_TOKEN)
meetup = MeetupClient(MEETUP_API_KEY)
twitter = TwitterClient(
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)

slack_oauth = SlackOAuthFlow(SLACK_CLIENT_ID, SLACK_CLIENT_SECRET)
github_oauth = GitHubOAuthFlow(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
