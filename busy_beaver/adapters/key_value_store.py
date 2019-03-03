from busy_beaver.extensions import db
from busy_beaver.models import KeyValueStore


class KeyValueStoreAdapter:
    """Wrapper around KeyValue Table"""

    def get(self, key: str) -> str:
        record = KeyValueStore.query.filter_by(key=key).first()
        if not record:
            raise ValueError(f"{key} does not exist in key-value store")
        return record.value.decode("utf-8")

    def put(self, key: str, data: str):
        new_item = KeyValueStore(key=key, value=data.encode("utf-8"))
        db.session.add(new_item)
        db.session.commit()
        return key

    def get_int(self, key: str) -> int:
        return int(self.get(key))

    def put_int(self, key: str, data: int):
        return self.put(key, str(data))
