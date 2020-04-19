from datetime import timedelta
import logging

import click

from .blueprint import github_bp
from .summary.workflow import fetch_github_summary_post_to_slack
from busy_beaver.exceptions import ValidationError
from busy_beaver.models import SlackInstallation
from busy_beaver.toolbox import utc_now_minus

logger = logging.getLogger(__name__)


@click.option("--workspace", required=True)  # Slack Workspace ID
@github_bp.cli.command("post_github_summary", help="Post a GitHub summary")
def post_github_summary_to_slack_cli(workspace: str):
    boundary_dt = utc_now_minus(timedelta(days=1))
    installation = SlackInstallation.query.filter_by(workspace_id=workspace).first()
    if not installation:
        raise ValidationError("workspace not found")

    # we should log that we did something somewhere
    # also keep track of how long a summary took
    # TODO once we are migrated over
    fetch_github_summary_post_to_slack(installation, boundary_dt)
