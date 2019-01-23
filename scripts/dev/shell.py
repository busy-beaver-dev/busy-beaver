import os

from busy_beaver import db  # noqa
from busy_beaver.adapters.github import GitHubAdapter
from busy_beaver.adapters.slack import SlackAdapter
from busy_beaver.github_stats import generate_summary  # noqa
from busy_beaver.models import *  # noqa

from busy_beaver.retweeter import get_tweets, post_tweets_to_slack # noqa


OAUTH_TOKEN = os.getenv("GITHUB_OAUTH_TOKEN")
github = GitHubAdapter(OAUTH_TOKEN)

SLACK_TOKEN = os.getenv("SLACK_BOTUSER_OAUTH_TOKEN")
slack = SlackAdapter(SLACK_TOKEN)

display_text = "busy-beaver Development Shell"
num_char = len(display_text)
print("*" * num_char)

print(display_text)
print("*" * num_char)
