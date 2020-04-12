from typing import Optional, Union

from busy_beaver.extensions import db
from busy_beaver.models import KeyValueStore


class KeyValueStoreClient:
    """Wrapper around KeyValue Table"""

    def get(self, installation_id: int, key: str) -> str:
        record = self._get_value_by_key(installation_id, key)
        if not record:
            raise ValueError(f"{key} does not exist in key-value store")
        return record.value.decode("utf-8")

    def put(self, installation_id: int, key: str, data: str):
        record = self._get_value_by_key(installation_id, key)
        if not record:
            record = KeyValueStore(
                installation_id=installation_id, key=key, value=data.encode("utf-8")
            )
        else:
            record.value = data.encode("utf-8")

        db.session.add(record)
        db.session.commit()
        return key

    def get_int(self, installation_id: int, key: str) -> int:
        return int(self.get(installation_id, key))

    def put_int(self, installation_id: int, key: str, data: int):
        return self.put(installation_id, key, str(data))

    def _get_value_by_key(
        self, installation_id: int, key: str
    ) -> Optional[Union[str, int]]:
        return KeyValueStore.query.filter_by(
            installation_id=installation_id, key=key
        ).first()
