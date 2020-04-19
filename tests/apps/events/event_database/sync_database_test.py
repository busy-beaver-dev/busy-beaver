import pytest

from busy_beaver.apps.events.event_database.sync_database import (
    classify_transaction_type,
)


@pytest.mark.unit
def test_classify_transaction_type():
    fetched_ids = [3, 4, 5, 6, 7, 10]
    database_ids = [3, 4, 5, 6, 7, 8, 9]

    result = classify_transaction_type(fetched_ids, database_ids)

    result.create == [10]
    result.delete == [8, 9]
    result.update == [3, 4, 5, 6, 7]
