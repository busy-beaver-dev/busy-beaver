from .apps.external_integrations.oauth_providers.slack import SlackOAuthFlow
from .adapters import (
    GitHubAdapter,
    KeyValueStoreAdapter,
    MeetupAdapter,
    SlackAdapter,
    TwitterAdapter,
)
from .config import (
    GITHUB_OAUTH_TOKEN,
    MEETUP_API_KEY,
    SLACK_TOKEN,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    SLACK_CLIENT_ID,
    SLACK_CLIENT_SECRET,
)

chipy_slack = SlackAdapter(SLACK_TOKEN)  # Default Workspace -- this is being phased out
github = GitHubAdapter(GITHUB_OAUTH_TOKEN)
kv_store = KeyValueStoreAdapter()
meetup = MeetupAdapter(MEETUP_API_KEY)
twitter = TwitterAdapter(
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)

slack_oauth = SlackOAuthFlow(SLACK_CLIENT_ID, SLACK_CLIENT_SECRET)
