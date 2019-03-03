from busy_beaver.extensions import db
from . import BaseModel


class ApiUser(BaseModel):
    """API User table"""

    __tablename__ = "api_user"

    def __repr__(self):
        return f"<API: {self.username}>"

    # Attributes
    username = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False, default="user")
