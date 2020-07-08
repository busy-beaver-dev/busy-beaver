from datetime import date, datetime, timedelta
import logging

import click
import pytz

from .blueprint import github_bp
from .summary.workflow import fetch_github_summary_post_to_slack
from busy_beaver.exceptions import ValidationError
from busy_beaver.extensions import db, rq
from busy_beaver.models import SlackInstallation, Task
from busy_beaver.toolbox import set_task_progress, utc_now_minus

logger = logging.getLogger(__name__)


@rq.job
def post_github_summary_message(workspace: str):
    installation = SlackInstallation.query.filter_by(workspace_id=workspace).first()
    if not installation:
        raise ValidationError("workspace not found")

    boundary_dt = utc_now_minus(timedelta(days=1))
    fetch_github_summary_post_to_slack(installation, boundary_dt)
    set_task_progress(100)


# currently we will only kick off one task, check which rows are active
# name this cli option, queue_github_summary_jobs_for_tomorrow
@click.option("--workspace", required=True, prompt="Slack workspace ID")
@github_bp.cli.command("post_github_summary", help="Post a GitHub summary")
def queue_post_github_summary_task(workspace: str):
    installation = SlackInstallation.query.filter_by(workspace_id=workspace).first()
    config = installation.github_summary_config
    time_to_post = _get_time_to_post(config)
    job = post_github_summary_message.schedule(time_to_post, workspace=workspace)

    task = Task(
        job_id=job.id,
        name="post_github_summary_message",
        task_state=Task.TaskState.SCHEDULED,
        data={"workspace_id": workspace},
    )
    db.session.add(task)
    db.session.commit()


# TODO end-to-end test
# mock this out with a datetime now and make sure task runs
def _get_time_to_post(config):
    tomorrow = date.today() + timedelta(days=1)
    dt_to_post = datetime.combine(tomorrow, config.summary_post_time)
    tz = pytz.timezone(config.summary_post_timezone)
    localized_dt = tz.localize(dt_to_post)
    return localized_dt.astimezone(pytz.utc)
