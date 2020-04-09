"""Update Events Database task

This task pulls a set of events from Meetup and performs the following action against
the set of future events in the database:
    - if event is new => create
    - if event is in the database, but not in the fetched events => delete
    - if event is in the database => update
"""

import logging
import time

import click

from ..blueprint import events_bp
from .sync_database import SyncEventDatabase
from busy_beaver.clients import meetup
from busy_beaver.config import MEETUP_GROUP_NAME
from busy_beaver.extensions import db, rq
from busy_beaver.models import ApiUser, Event, SyncEventDatabaseTask

logger = logging.getLogger(__name__)


@click.option("--group_name", required=True)
@events_bp.cli.command("sync_events_database", help="Sync Events Database")
def sync_events_database_cli(group_name: str):
    sync_database_with_fetched_events(group_name)


def start_sync_event_database_task(task_owner: ApiUser):
    logger.info("[Busy Beaver] Kick off fetch meetup events task")

    group_name = MEETUP_GROUP_NAME
    job = sync_database_with_fetched_events.queue(group_name)

    task = SyncEventDatabaseTask(
        job_id=job.id,
        name="Poll Meetup",
        description="Poll Meetup for events",
        user=task_owner,
        data={"group_name": group_name},
    )
    db.session.add(task)
    db.session.commit()


@rq.job
def sync_database_with_fetched_events(group_name):
    fetched_events = meetup.get_events(group_name, count=20)

    current_epoch_time = int(time.time())
    database_events = Event.query.filter(Event.start_epoch > current_epoch_time).all()

    sync_database = SyncEventDatabase(fetched_events, database_events)
    sync_database.perform()
