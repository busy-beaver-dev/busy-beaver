import os

from busy_beaver import create_app
from busy_beaver.extensions import db
from busy_beaver.models import SlackInstallation

# load config
workspace_id = os.getenv("SLACK_DEV_WORKSPACE_ID", None)
bot_token = os.getenv("SLACK_BOTUSER_OAUTH_TOKEN", None)
authorizing_user_id = os.getenv("SLACK_DEV_AUTHORIZING_USER_ID", "U5FTQ3QRZ")
bot_user_id = os.getenv("SLACK_DEV_BOT_USER_ID", "UEGGXQ5EF")
if not bot_token or not workspace_id:
    exit

# create flask application context
app = create_app()
ctx = app.app_context()
ctx.push()

# create or update record
installation = SlackInstallation.query.filter_by(workspace_id=workspace_id).first()
if installation:
    installation.patch(
        data={
            "authorizing_user_id": authorizing_user_id,
            "bot_access_token": bot_token,
            "bot_user_id": bot_user_id,
            "workspace_id": workspace_id,
        }
    )
else:
    installation = SlackInstallation(
        access_token="access_token",
        authorizing_user_id=authorizing_user_id,
        bot_access_token=bot_token,
        bot_user_id=bot_user_id,
        scope="test-scope",
        workspace_id=workspace_id,
        workspace_name="Development Environment",
        state="active",
    )

db.session.add(installation)
db.session.commit()
