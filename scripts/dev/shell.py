from datetime import timedelta
import os

from busy_beaver import db  # noqa
from busy_beaver.adapters.github import GitHubAdapter  # noqa
from busy_beaver.adapters.utilities import date_subtract  # noq
from busy_beaver.github_stats import generate_summary  # noqa
from busy_beaver.models import *  # noqa
from busy_beaver.post_summary_stats import post_summary  # noqa


oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")
github = GitHubAdapter(oauth_token)

boundary_dt = date_subtract(timedelta(days=1))

display_text = "busy-beaver Development Shell"
num_char = len(display_text)
print("*" * num_char)
print(display_text)
print("*" * num_char)
