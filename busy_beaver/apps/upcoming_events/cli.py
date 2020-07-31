import calendar
from datetime import date, datetime, timedelta
import logging

import pytz

from .blueprint import events_bp
from .sync_database import sync_database_with_fetched_events
from .workflow import post_upcoming_events_message
from busy_beaver.extensions import db
from busy_beaver.models import Task, UpcomingEventsConfiguration

logger = logging.getLogger(__name__)


@events_bp.cli.command("sync_events_database", help="Sync Events Database")
def sync_events_database_cli():
    all_active_configs = UpcomingEventsConfiguration.query.filter_by(enabled=True)
    for config in all_active_configs:
        for group in config.groups:
            sync_database_with_fetched_events(group)


@events_bp.cli.command(
    "queue_post_upcoming_events_jobs", help="Queue Upcoming Events jobs for tomorrow"
)
def queue_upcoming_events_jobs_for_tomorrow():
    tomorrow = date.today() + timedelta(days=1)
    day_of_week = calendar.day_name[tomorrow.weekday()]

    all_active_configs = UpcomingEventsConfiguration.query.filter_by(
        enabled=True, post_day_of_week=day_of_week
    )

    for config in all_active_configs:
        time_to_post = _get_time_to_post(config)
        if not time_to_post:
            continue

        job = post_upcoming_events_message.schedule(time_to_post, config_id=config.id)
        task = Task(
            job_id=job.id,
            name="post_upcoming_events_message",
            task_state=Task.TaskState.SCHEDULED,
            time_to_post=time_to_post,
            data={"config_id": config.id},
        )
        db.session.add(task)
        db.session.commit()


def _get_time_to_post(config):
    # TODO state machine can remove this
    if not config.post_time or not config.post_timezone:
        extra = {"workspace_id": config.slack_installation.workspace_id}
        logger.error("No time to post configuration", extra=extra)
        return None
    tomorrow = date.today() + timedelta(days=1)
    dt_to_post = datetime.combine(tomorrow, config.post_time)
    localized_dt = config.post_timezone.localize(dt_to_post)
    return localized_dt.astimezone(pytz.utc)
