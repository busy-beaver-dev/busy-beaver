from simplekv.db.sql import SQLAlchemyStore
from .. import db
from ..adapters.key_value_store import KeyValueStore

store = SQLAlchemyStore(db.engine, db.metadata, 'kv_store')
kv_store = KeyValueStore(store)
