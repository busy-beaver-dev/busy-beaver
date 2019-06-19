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
        EncryptedType(db.String, SECRET_KEY, AesEngine, "pkcs5"), nullable=True
    )
    authorizing_user_id = db.Column(db.String(300), nullable=True)
    bot_access_token = db.Column(
        EncryptedType(db.String, SECRET_KEY, AesEngine, "pkcs5"), nullable=True
    )
    bot_user_id = db.Column(
        EncryptedType(db.String, SECRET_KEY, AesEngine, "pkcs5"), nullable=True
    )
    scope = db.Column(db.String(300), nullable=True)
    state = db.Column(db.String(36), nullable=True, index=True)
    workspace_id = db.Column(db.String(20), nullable=True, index=True)
    workspace_name = db.Column(db.String(255), nullable=True)
