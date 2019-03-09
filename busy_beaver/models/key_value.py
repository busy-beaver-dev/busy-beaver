from busy_beaver.extensions import db
from . import BaseModel


class KeyValueStore(BaseModel):
    """Key Value store by slack workspace id

    Keeps track of required values for each workspace"""

    __tablename__ = "key_value_store"

    def __repr__(self):
        return f"<KeyValueStore: {self.key} {self.value}>"

    # Attributes
    # TODO add slack workspace id once when we start being more than single tenant
    key = db.Column(db.String(255), nullable=False, unique=True)
    value = db.Column(db.LargeBinary(), nullable=False)
