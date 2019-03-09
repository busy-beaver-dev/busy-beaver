from typing import Optional, Union
from busy_beaver.extensions import db
from busy_beaver.models import KeyValueStore


class KeyValueStoreAdapter:
    """Wrapper around KeyValue Table"""

    def get(self, key: str) -> str:
        record = self._get_value_by_key(key)
        if not record:
            raise ValueError(f"{key} does not exist in key-value store")
        return record.value.decode("utf-8")

    def put(self, key: str, data: str):
        record = self._get_value_by_key(key)
        if not record:
            record = KeyValueStore(key=key, value=data.encode("utf-8"))
        else:
            record.value = data.encode("utf-8")

        db.session.add(record)
        db.session.commit()
        return key

    def get_int(self, key: str) -> int:
        return int(self.get(key))

    def put_int(self, key: str, data: int):
        return self.put(key, str(data))

    def _get_value_by_key(self, key: str) -> Optional[Union[str, int]]:
        return KeyValueStore.query.filter_by(key=key).first()
