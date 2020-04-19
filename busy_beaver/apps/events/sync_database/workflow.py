"""Update Events Database task

This task pulls a set of events from Meetup and performs the following action against
the set of future events in the database:
    - if event is new => create
    - if event is in the database, but not in the fetched events => delete
    - if event is in the database => update
"""

import logging
import time

from .sync_database import SyncEventDatabase
from busy_beaver.clients import meetup
from busy_beaver.models import Event

logger = logging.getLogger(__name__)


def sync_database_with_fetched_events(group_name):
    fetched_events = meetup.get_events(group_name, count=20)

    current_epoch_time = int(time.time())
    database_events = Event.query.filter(Event.start_epoch > current_epoch_time).all()

    sync_database = SyncEventDatabase(fetched_events, database_events)
    sync_database.perform()
