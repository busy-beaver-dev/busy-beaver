from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from . import BaseModel
from busy_beaver.extensions import db

secret = "blah"  # TODO pull this in from env variable


class SlackInstallation(BaseModel):
    """Keep track of each installation of Slack integration"""

    __tablename__ = "slack_installation"

    def __repr__(self):  # pragma: no cover
        return f"<SlackInstallation: {self.workspace_name}>"

    # Attributes
    # TODO find limits of each field in slack
    access_token = db.Column(EncryptedType(db.String, secret, AesEngine, "pkcs5"))
    authorizing_user_id = db.Column(db.String(300), nullable=False)
    bot_access_token = db.Column(EncryptedType(db.String, secret, AesEngine, "pkcs5"))
    bot_user_id = db.Column(EncryptedType(db.String, secret, AesEngine, "pkcs5"))
    scope = db.Column(db.String(300), nullable=False)
    workspace_id = db.Column(db.String(300), nullable=False)
    workspace_name = db.Column(db.String(300), nullable=False)
