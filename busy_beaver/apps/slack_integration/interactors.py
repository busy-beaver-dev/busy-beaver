from .models import SlackInstallation


def make_slack_response(
    response_type="ephemeral", text="", attachments=None, blocks=None
):
    return {
        "response_type": response_type,
        "text": text,
        "attachments": [attachments] if attachments else [],
        "blocks": blocks if blocks else [],
    }


def generate_help_text(installation: SlackInstallation):
    help_text = (
        "Busy Beaver is a Community Engagement bot.\n"
        "\n"
        "Some commands I understand:\n"
    )

    if installation.upcoming_events_config:
        if installation.upcoming_events_config.enabled:
            help_text += (
                "`/busybeaver next`: Retrieve next event\n"
                "`/busybeaver events`: Retrieve list of upcoming event\n"
            )

    if installation.github_summary_config:
        if installation.github_summary_config.enabled:
            help_text += (
                "`/busybeaver connect`: Connect GitHub Account\n"
                "`/busybeaver reconnect`: Connect to difference GitHub Account\n"
                "`/busybeaver disconnect`: Disconenct GitHub Account\n"
            )

    help_text += "`/busybeaver help`: Display help text"
    return help_text
