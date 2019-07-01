from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from . import BaseModel
from busy_beaver.config import SECRET_KEY
from busy_beaver.extensions import db


class SlackInstallation(BaseModel):
    """Keep track of each installation of Slack integration"""

    __tablename__ = "slack_installation"

    def __repr__(self):  # pragma: no cover
        return f"<SlackInstallation: {self.workspace_name}>"

    # Attributes
    access_token = db.Column(
        EncryptedType(db.String, SECRET_KEY, AesEngine, "pkcs5"), nullable=False
    )
    authorizing_user_id = db.Column(db.String(300), nullable=False)
    bot_access_token = db.Column(
        EncryptedType(db.String, SECRET_KEY, AesEngine, "pkcs5"), nullable=False
    )
    bot_user_id = db.Column(
        EncryptedType(db.String, SECRET_KEY, AesEngine, "pkcs5"), nullable=False
    )
    scope = db.Column(db.String(300), nullable=False)
    workspace_id = db.Column(db.String(20), index=True, nullable=False)
    workspace_name = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(20), nullable=False, default="installed")

    # Relationships
    github_summary_users = db.relationship(
        "GitHubSummaryUser", back_populates="installation"
    )
    github_summary_config = db.relationship(
        "GitHubSummaryConfiguration", back_populates="slack_installation", uselist=False
    )
