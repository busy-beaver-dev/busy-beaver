from datetime import timedelta
import os

from IPython import embed

from busy_beaver.adapters.github import GitHubAdapter  # noqa
from busy_beaver.adapters.utilities import subtract_timedelta  # noqa
from busy_beaver.userstats.script import recent_activity_text  # noqa


oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")
github = GitHubAdapter(oauth_token)

boundary_dt = subtract_timedelta(timedelta(days=1))

embed()
