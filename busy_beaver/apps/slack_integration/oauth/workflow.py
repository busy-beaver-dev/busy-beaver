from datetime import time

from busy_beaver.clients import slack_oauth
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.extensions import db
from busy_beaver.models import SlackInstallation


def verify_callback_and_save_tokens_in_database(callback_url, state):
    oauth_details = slack_oauth.process_callback(callback_url, state)
    oauth_dict = oauth_details._asdict()

    # TODO update or create seems like a useful helper function
    existing_installation = SlackInstallation.query.filter_by(
        workspace_id=oauth_details.workspace_id
    ).first()
    if existing_installation:
        existing_installation.patch(oauth_dict)
        installation = existing_installation
    else:
        installation = SlackInstallation(**oauth_dict)

    db.session.add(installation)
    db.session.commit()
    return installation


ONBOARDING_MESSAGE = (
    "Hi <@{slack_id}>! :wave:\n\n"
    "I'm here to help engage tech-focused Slack communities.\n"
    "Thank you for taking part in our beta program. :pray:\n\n"
    ":zap: To get started `/invite` me to a public channel\n"
    ":bulb: I recommend creating `#busy-beaver`"
)


def send_welcome_message(installation: SlackInstallation):
    slack = SlackClient(installation.bot_access_token)
    user_id = installation.authorizing_user_id
    slack.dm(ONBOARDING_MESSAGE.format(slack_id=user_id), user_id=user_id)


CONFIRMED_MESSAGE = (
    "Thanks for the invite! I will post daily summaries in <#{channel}>\n\n"
    "What time should I post the daily GitHub summary?"
)


def send_configuration_message(installation: SlackInstallation):
    slack = SlackClient(installation.bot_access_token)
    user_id = installation.authorizing_user_id
    channel = installation.github_summary_config.channel
    slack.dm(CONFIRMED_MESSAGE.format(channel=channel), user_id=user_id)


ACTIVE_MESSAGE = (
    "Confirmed; I will post daily summaries at {time}.\n\n"
    "Busy Beaver is now active! :tada: \n\n"
    "You can use the following text to publicize the bot:\n"
    "> Busy Beaver is a community engagement bot that shares daily "
    "sumarries of public GitHub activity for registered users. "
    "Find out what everybody's working on in <#{channel}>!"
)


def save_configuration(installation: SlackInstallation, time_to_post: time):
    slack = SlackClient(installation.bot_access_token)
    user_id = installation.authorizing_user_id
    tz = slack.get_user_timezone(user_id)

    github_summary_config = installation.github_summary_config
    github_summary_config.time_to_post = str(time_to_post)
    github_summary_config.timezone_info = tz._asdict()
    db.session.add(github_summary_config)
    db.session.commit()

    channel = github_summary_config.channel
    slack.dm(
        ACTIVE_MESSAGE.format(time=str(time_to_post), channel=channel), user_id=user_id
    )


GITHUB_SUMMARY_CHANNEL_JOIN_MESSAGE = (
    "Welcome to <#{channel}>! I'm Busy Beaver. "
    "I post daily summaries of public GitHub activity "
    "in this channel.\n\n"
    "To connect your GitHub account and share activity, "
    "please register using `/busybeaver connect`."
)
