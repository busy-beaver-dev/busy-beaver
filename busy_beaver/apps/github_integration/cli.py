from datetime import date, datetime, timedelta
import logging

import click
import pytz

from .blueprint import github_bp
from .summary.workflow import post_github_summary_message
from busy_beaver.exceptions import GitHubSummaryException
from busy_beaver.extensions import db
from busy_beaver.models import SlackInstallation, Task

logger = logging.getLogger(__name__)


# currently we will only kick off one task, check which rows are active
@click.option("--workspace", required=True, prompt="Slack workspace ID")
@github_bp.cli.command(
    "queue_github_summary_jobs", help="Queue GitHub summary jobs for tomorrow"
)
def queue_github_summary_jobs_for_tomorrow(workspace: str):
    installation = SlackInstallation.query.filter_by(workspace_id=workspace).first()
    time_to_post = _get_time_to_post(installation)
    job = post_github_summary_message.schedule(time_to_post, workspace=workspace)

    task = Task(
        job_id=job.id,
        name="post_github_summary_message",
        task_state=Task.TaskState.SCHEDULED,
        data={"workspace_id": workspace, "time_to_post": time_to_post},
    )
    db.session.add(task)
    db.session.commit()


def _get_time_to_post(installation):
    config = installation.github_summary_config
    if not config.summary_post_time or not config.summary_post_timezone:
        extra = {"workspace_id": installation.workspace_id}
        raise GitHubSummaryException("Time to post configuration ", extra=extra)
    tomorrow = date.today() + timedelta(days=1)
    dt_to_post = datetime.combine(tomorrow, config.summary_post_time)
    localized_dt = config.summary_post_timezone.localize(dt_to_post)
    return localized_dt.astimezone(pytz.utc)
