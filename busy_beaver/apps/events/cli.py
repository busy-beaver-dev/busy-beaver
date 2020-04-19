import logging

import click

from .blueprint import events_bp
from .sync_database import sync_database_with_fetched_events
from .upcoming_events import generate_upcoming_events_message
from busy_beaver.clients import SlackClient
from busy_beaver.models import SlackInstallation

logger = logging.getLogger(__name__)


@click.option("--count", default=5, required=True, help="Number of events to post")
@click.option("--group_name", required=True, help="Meetup group name")
@click.option("--channel", required=True, help="Slack channel")
@click.option("--workspace", required=True, help="Slack workspace ID")
@events_bp.cli.command(
    "post_upcoming_events", help="Post Upcoming Events Summary to Slack channel"
)
def post_upcoming_events_message_to_slack_cli(
    workspace: str, channel: str, group_name: str, count: int
):
    blocks = generate_upcoming_events_message(group_name, count)
    installation = SlackInstallation.query.filter_by(workspace_id=workspace).first()
    slack = SlackClient(installation.bot_access_token)
    slack.post_message(blocks=blocks, channel=channel)


@click.option("--group_name", required=True, help="Meetup group name")
@events_bp.cli.command("sync_events_database", help="Sync Events Database")
def sync_events_database_cli(group_name: str):
    sync_database_with_fetched_events(group_name)
