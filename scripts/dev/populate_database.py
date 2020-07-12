from datetime import time
import os

from busy_beaver import create_app
from busy_beaver.extensions import db
from busy_beaver.models import (
    Event,
    GitHubSummaryConfiguration,
    SlackInstallation,
    UpcomingEventsConfiguration,
)
from tests._utilities.factories.event import Event as EventFactory

# load config
workspace_id = os.getenv("SLACK_DEV_WORKSPACE_ID", None)
github_summary_channel = os.getenv("SLACK_DEV_WORKSPACE_GITHUB_SUMMARY_CHANNEL", None)
upcoming_events_channel = os.getenv("SLACK_DEV_WORKSPACE_UPCOMING_EVENTS_CHANNEL", None)
bot_token = os.getenv("SLACK_BOTUSER_OAUTH_TOKEN", None)
authorizing_user_id = os.getenv("SLACK_DEV_AUTHORIZING_USER_ID", "U5FTQ3QRZ")
bot_user_id = os.getenv("SLACK_DEV_BOT_USER_ID", "UEGGXQ5EF")
if (
    not github_summary_channel
    or not upcoming_events_channel
    or not bot_token
    or not workspace_id
):
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

if not installation.github_summary_config:
    config = GitHubSummaryConfiguration(
        enabled=True,
        slack_installation=installation,
        channel=github_summary_channel,
        summary_post_time=time(14, 00),
        summary_post_timezone="America/Chicago",
    )
    db.session.add(config)
    db.session.commit()

# update events database
events = Event.query.all()
if not events:
    create_event = EventFactory(db.session)
    create_event()

if not installation.upcoming_events_config:
    config = UpcomingEventsConfiguration(
        enabled=True, slack_installation=installation, channel=upcoming_events_channel
    )
    db.session.add(config)
    db.session.commit()
