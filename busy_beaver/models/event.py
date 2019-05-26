from . import BaseModel
from busy_beaver.extensions import db


class Event(BaseModel):
    """Event table for storing information about past and future meetups"""

    __tablename__ = "event"

    def __repr__(self):
        return f"<Event: {self.name}>"

    # Attributes
    remote_id = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    utc_epoch = db.Column(db.Integer, nullable=False)
