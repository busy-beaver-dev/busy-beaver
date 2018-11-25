from sqlalchemy.ext.declarative import declared_attr

from .. import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        onupdate=db.func.current_timestamp(),
        default=db.func.current_timestamp(),
    )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def patch(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)
