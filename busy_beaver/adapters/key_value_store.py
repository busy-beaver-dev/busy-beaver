from simplekv.db.sql import SQLAlchemyStore


class KeyValueStore:
    """Wrapper around simplekv

    Takes care of encoding/decoding bytes
    """

    def __init__(self, store: SQLAlchemyStore):
        self.store = store

    def get(self, key: str) -> str:
        return self.store.get(key).decode("utf-8")

    def get_int(self, key: str) -> int:
        return int(self.get(key))

    def put(self, key: str, data: str):
        return self.store.put(key, data.encode("utf-8"))

    def put_int(self, key: str, data: int):
        return self.put(key, str(data))
