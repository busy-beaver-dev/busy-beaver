from .adapters import GitHubAdapter, KeyValueStoreAdapter, MeetupAdapter, TwitterAdapter
from .config import (
    GITHUB_OAUTH_TOKEN,
    MEETUP_API_KEY,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
)

github = GitHubAdapter(GITHUB_OAUTH_TOKEN)
kv_store = KeyValueStoreAdapter()
meetup = MeetupAdapter(MEETUP_API_KEY)
twitter = TwitterAdapter(
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)
