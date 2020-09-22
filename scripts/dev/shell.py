import os

from busy_beaver import create_app
from busy_beaver.common.wrappers import (
    GitHubClient,
    KeyValueStoreClient,
    MeetupClient,
    SlackClient,
    YouTubeClient,
)
from busy_beaver.extensions import db, rq  # noqa
from busy_beaver.models import *  # noqa

# create flask application context
app = create_app()
ctx = app.app_context()
ctx.push()

# configure adapters
OAUTH_TOKEN = os.getenv("GITHUB_OAUTH_TOKEN")
github = GitHubClient(OAUTH_TOKEN)

SLACK_TOKEN = os.getenv("SLACK_BOTUSER_OAUTH_TOKEN")
slack = SlackClient(SLACK_TOKEN)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = YouTubeClient(api_key=YOUTUBE_API_KEY)

MEETUP_API_KEY = os.getenv("MEETUP_API_KEY")
meetup = MeetupClient(MEETUP_API_KEY)

kv = KeyValueStoreClient()

# log to console
display_text = "Busy Beaver Development Shell"
num_char = len(display_text)
print("*" * num_char)
print(display_text)
print("*" * num_char)
