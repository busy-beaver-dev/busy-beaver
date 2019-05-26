import logging
import time
from typing import List

from busy_beaver import meetup
from busy_beaver.config import MEETUP_GROUP_NAME
from busy_beaver.extensions import db
from busy_beaver.models import Event

logger = logging.getLogger(__name__)


def add_new_events_to_database():
    fetched_events = meetup.get_events(MEETUP_GROUP_NAME, count=20)
    fetched_remote_id = [event.id for event in fetched_events]

    remote_ids_in_database = _fetch_events_from_database()
    ids_to_add = set(fetched_remote_id) - set(remote_ids_in_database)
    events_to_add: List[Event] = [
        event for event in fetched_events if event.id in ids_to_add
    ]

    _insert_events_into_database(events_to_add)


def _fetch_events_from_database():
    current_epoch_time = int(time.time())
    upcoming_events_in_db = Event.query.filter(
        Event.utc_epoch > current_epoch_time
    ).all()
    return [event.remote_id for event in upcoming_events_in_db]


def _insert_events_into_database(events):
    num_records_created = 0
    for event in events:
        record = event.create_event_record()
        db.session.add(record)
        num_records_created += 1
    else:
        db.session.commit()
        logger.info("{0} events saved to the database".format(num_records_created))
