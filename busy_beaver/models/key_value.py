from . import BaseModel
from busy_beaver.extensions import db


class KeyValueStore(BaseModel):
    """Key Value store by slack workspace id

    Keeps track of required values for each workspace"""

    __tablename__ = "key_value_store"

    def __repr__(self):  # pragma: no cover
        workspace_name = {self.slack_installation.workspace_name}
        return f"<KeyValueStore: {workspace_name} {self.key} {self.value}>"

    # Attributes
    installation_id = db.Column(
        db.Integer,
        db.ForeignKey("slack_installation.id", name="fk_installation_id"),
        nullable=True,
    )
    key = db.Column(db.String(255), nullable=False, unique=True)
    value = db.Column(db.LargeBinary(), nullable=False)

    # Relationships
    slack_installation = db.relationship(
        "SlackInstallation", back_populates="key_value_pairs"
    )
