from .models import SlackInstallation
from busy_beaver.common.wrappers import SlackClient


def make_slack_response(
    response_type="ephemeral", text="", attachments=None, blocks=None
):
    return {
        "response_type": response_type,
        "text": text,
        "attachments": [attachments] if attachments else [],
        "blocks": blocks if blocks else [],
    }


def generate_help_text(installation: SlackInstallation, user_id: str) -> str:
    help_text = "Busy Beaver is a Community Engagement bot.\n\n"
    github_summary_config = installation.github_summary_config
    upcoming_events_config = installation.upcoming_events_config

    if github_summary_config:
        if github_summary_config.enabled:
            help_text += (
                f"See what projects other members of your community "
                f"are working on in <#{github_summary_config.channel}>.\n\n"
            )

    help_text += "Some commands I understand:\n"

    if upcoming_events_config:
        if upcoming_events_config.enabled:
            help_text += (
                "`/busybeaver next`: Retrieve next event\n"
                "`/busybeaver events`: Retrieve list of upcoming events\n"
            )

    if github_summary_config:
        if github_summary_config.enabled:
            help_text += (
                "`/busybeaver connect`: Connect GitHub Account\n"
                "`/busybeaver reconnect`: Connect to different GitHub Account\n"
                "`/busybeaver disconnect`: Disconenct GitHub Account\n"
            )

    slack = SlackClient(installation.bot_access_token)
    is_admin = slack.is_admin(user_id)
    if is_admin:
        help_text += "`/busybeaver settings`: View/Modify Busy Beaver settings\n"

    help_text += "`/busybeaver help`: Display help text"
    return help_text
