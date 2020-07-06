from busy_beaver.apps.slack_integration.models import SlackInstallation, SlackUser
from busy_beaver.common.wrappers import SlackClient


def generate_settings_context(user: SlackUser):
    installation: SlackInstallation = user.installation
    slack = SlackClient(installation.bot_access_token)

    is_admin = slack.is_admin(user.slack_id)

    github_summary_config = installation.github_summary_config
    channel = github_summary_config.channel
    channel_info = slack.channel_details(channel)

    return {"is_admin": is_admin, "github_summary": {"channel": channel_info["name"]}}
