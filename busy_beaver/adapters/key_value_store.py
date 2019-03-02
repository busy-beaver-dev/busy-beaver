from busy_beaver.extensions import db
from busy_beaver.models import KeyValueStore


class KeyValueStoreAdapter:
    """Wrapper around simplekv
    Takes care of encoding/decoding bytes
    """

    def get(self, key: str) -> str:
        # TODO add check for item not existing
        record = KeyValueStore.query.filter_by(key=key).first()
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
