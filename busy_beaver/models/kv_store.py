from simplekv.db.sql import SQLAlchemyStore
from .. import db

store = SQLAlchemyStore(db.engine, db.metadata, 'kv_store')
