import os

from busy_beaver import create_app
from busy_beaver.adapters import (
    GitHubAdapter,
    KeyValueStoreAdapter,
    SlackAdapter,
    TwitterAdapter,
)
from busy_beaver.extensions import db, rq  # noqa
from busy_beaver.models import *  # noqa

# create flask application context
app = create_app()
ctx = app.app_context()
ctx.push()

# configure adapters
OAUTH_TOKEN = os.getenv("GITHUB_OAUTH_TOKEN")
github = GitHubAdapter(OAUTH_TOKEN)

slack = SlackAdapter(app.config['SLACK_TOKEN'])

twitter = TwitterAdapter(
    app.config['WITTER_CONSUMER_KEY'],
    app.config['TWITTER_CONSUMER_SECRET'],
    app.config['TWITTER_ACCESS_TOKEN'],
    app.config['TWITTER_ACCESS_TOKEN_SECRET'],
)

kv = KeyValueStoreAdapter()

# log to console
display_text = "busy-beaver Development Shell"
num_char = len(display_text)
print("*" * num_char)
print(display_text)
print("*" * num_char)
