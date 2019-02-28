from simplekv.db.sql import SQLAlchemyStore

from busy_beaver import app
from busy_beaver.extensions import db

with app.app_context():
    key_value_store = SQLAlchemyStore(db.engine, db.metadata, 'kv_store')
