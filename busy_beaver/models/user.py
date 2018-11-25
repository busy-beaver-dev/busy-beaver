from .. import db
from . import BaseModel


class User(BaseModel):
    """User table"""

    def __repr__(self):
        return f"<User slack: {self.slack} github: {self.github}>"

    # Attributes
    slack = db.Column(db.String(300), nullable=False)
    github = db.Column(db.String(300), nullable=False)
