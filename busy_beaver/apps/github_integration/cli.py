from datetime import date, datetime, timedelta
import logging

import pytz

from .blueprint import github_bp
from .models import GitHubSummaryConfiguration
from .summary.workflow import post_github_summary_message
from busy_beaver.exceptions import GitHubSummaryException
from busy_beaver.extensions import db
from busy_beaver.models import Task

logger = logging.getLogger(__name__)


@github_bp.cli.command(
    "queue_github_summary_jobs", help="Queue GitHub summary jobs for tomorrow"
)
def queue_github_summary_jobs_for_tomorrow():
    all_active_configs = GitHubSummaryConfiguration.query.filter_by(enabled=True)

    for config in all_active_configs:
        workspace_id = config.slack_installation.workspace_id
        time_to_post = _get_time_to_post(config)
        job = post_github_summary_message.schedule(
            time_to_post, workspace_id=workspace_id
        )
        task = Task(
            job_id=job.id,
            name="post_github_summary_message",
            task_state=Task.TaskState.SCHEDULED,
            data={
                "workspace_id": workspace_id,
                "time_to_post": time_to_post.isoformat(),
            },
        )
        db.session.add(task)
        db.session.commit()


def _get_time_to_post(config):
    if not config.summary_post_time or not config.summary_post_timezone:
        extra = {"workspace_id": config.slack_installation.workspace_id}
        raise GitHubSummaryException("Time to post configuration ", extra=extra)
    tomorrow = date.today() + timedelta(days=1)
    dt_to_post = datetime.combine(tomorrow, config.summary_post_time)
    localized_dt = config.summary_post_timezone.localize(dt_to_post)
    return localized_dt.astimezone(pytz.utc)
