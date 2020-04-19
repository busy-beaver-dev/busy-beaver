import click

from .blueprint import events_bp
from .workflow import generate_upcoming_events_message
from busy_beaver.clients import SlackClient
from busy_beaver.models import SlackInstallation


@click.option("--count", default=5, required=True)
@click.option("--group_name", required=True)
@click.option("--channel", required=True)
@click.option("--workspace", required=True)
@events_bp.cli.command("post_upcoming_events", help="Post Upcoming Events Summary")
def post_upcoming_events_message_to_slack_cli(
    workspace: str, channel: str, group_name: str, count: int
):
    blocks = generate_upcoming_events_message(group_name, count)
    installation = SlackInstallation.query.filter_by(workspace_id=workspace).first()
    slack = SlackClient(installation.bot_access_token)
    slack.post_message(blocks=blocks, channel=channel)
