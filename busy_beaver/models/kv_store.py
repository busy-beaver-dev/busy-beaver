from simplekv.db.sql import SQLAlchemyStore
from .. import db

kv_store = SQLAlchemyStore(db.engine, db.metadata, 'kv_store')
