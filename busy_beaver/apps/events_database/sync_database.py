import logging
from typing import Dict, List, NamedTuple

from busy_beaver.adapters.meetup import EventDetails
from busy_beaver.extensions import db
from busy_beaver.models import Event

logger = logging.getLogger(__name__)


class TransactionType(NamedTuple):
    create: list
    update: list
    delete: list


class UpdateRecord(NamedTuple):
    current: Event
    new: EventDetails


class SyncDatabaseWithEvents:
    def __init__(
        self, fetched_events: List[EventDetails], database_events: List[Event]
    ):
        self.fetched_events_map: Dict[str, EventDetails] = {
            event.id: event for event in fetched_events
        }
        self.database_events_map: Dict[str, Event] = {
            event.remote_id: event for event in database_events
        }
        self.transactions = classify_transaction_type(
            fetched_ids=self.fetched_events_map.keys(),
            database_ids=self.database_events_map.keys(),
        )

    def perform(self):
        self._add_events_to_database()
        self._delete_events_from_database()
        self._update_events_in_database()

    def _add_events_to_database(self):
        events = [self.fetched_events_map[id_] for id_ in self.transactions.create]

        num_created = 0
        for event in events:
            record = event.create_event_record()
            db.session.add(record)
            num_created += 1
        else:
            db.session.commit()
            logger.info("{0} events saved to the database".format(num_created))

    def _delete_events_from_database(self):
        events = [self.database_events_map[id_] for id_ in self.transactions.delete]

        num_deleted = 0
        for event in events:
            db.session.delete(event)
            num_deleted += 1
        else:
            db.session.commit()
            logger.info("{0} events deleted from the database".format(num_deleted))

    def _update_events_in_database(self):
        events = [
            UpdateRecord(self.database_events_map[id_], self.fetched_events_map[id_])
            for id_ in self.transactions.update
        ]

        num_updated = 0
        for event_details in events:
            event_in_db = event_details.current
            fetched_event = event_details.new.create_event_record_dict()

            event_in_db.patch(fetched_event)
            db.session.add(event_in_db)
            num_updated += 1
        else:
            db.session.commit()
            logger.info("{0} events updated in the database".format(num_updated))


# TODO: look into testing with hypothesis
def classify_transaction_type(fetched_ids: list, database_ids: list):
    fetched_event_ids = set(fetched_ids)
    database_event_ids = set(database_ids)

    add_ids = list(fetched_event_ids - database_event_ids)
    delete_ids = list(database_event_ids - fetched_event_ids)
    update_ids = list(database_event_ids.intersection(fetched_event_ids))

    return TransactionType(create=add_ids, update=update_ids, delete=delete_ids)
