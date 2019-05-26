from . import BaseModel
from busy_beaver.extensions import db


class ApiUser(BaseModel):
    """API User table"""

    __tablename__ = "api_user"

    def __repr__(self):  # pragma: no cover
        return f"<API: {self.username}>"

    # Attributes
    username = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False, default="user")

    # Relationships
    tasks = db.relationship("Task", back_populates="user")
