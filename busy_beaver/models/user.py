from .. import db
from . import BaseModel


class User(BaseModel):
    """User table"""

    def __repr__(self):
        return f"<User slack: {self.slack_id} github: {self.github_id}>"

    # Attributes
    # this is unique
    slack_id = db.Column(db.String(300), nullable=False)

    github_id = db.Column(db.String(300), nullable=True)
    github_state = db.Column(db.String(36), nullable=True)
    github_access_token = db.Column(db.String(100), nullable=True)
