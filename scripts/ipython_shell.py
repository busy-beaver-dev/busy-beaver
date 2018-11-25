from datetime import timedelta
import os

from IPython import embed

from busy_beaver.adapters.github import GitHubAdapter  # noqa
from busy_beaver.adapters.utilities import subtract_timedelta  # noqa
from busy_beaver.userstats.script import recent_activity_text  # noqa

from busy_beaver import db  # noqa
from busy_beaver.models import *  # noqa


def create_db():
    # TODO need to check existence test?
    db.create_all()


oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")
github = GitHubAdapter(oauth_token)

boundary_dt = subtract_timedelta(timedelta(days=1))

display_text = "Busy Beaver Development Shell"
num_char = len(display_text)
print("*" * num_char)
print(display_text)
print("*" * num_char)

embed()  # start IPython shell
