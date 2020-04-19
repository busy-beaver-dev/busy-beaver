from sqlalchemy.ext.declarative import declared_attr

from busy_beaver.extensions import db


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


class KeyValueStore(BaseModel):
    """Key Value store by slack workspace id

    Keeps track of required values for each workspace"""

    __tablename__ = "key_value_store"

    def __repr__(self):  # pragma: no cover
        workspace_name = self.slack_installation.workspace_name
        return f"<KeyValueStore: {workspace_name} {self.key} {self.value}>"

    # Attributes
    installation_id = db.Column(
        db.Integer,
        db.ForeignKey("slack_installation.id", name="fk_installation_id"),
        nullable=False,
    )
    key = db.Column(db.String(255), nullable=False, unique=True)
    value = db.Column(db.LargeBinary(), nullable=False)

    # Relationships
    slack_installation = db.relationship(
        "SlackInstallation", back_populates="key_value_pairs"
    )
