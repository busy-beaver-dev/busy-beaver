from datetime import time
import logging
from typing import NamedTuple

from busy_beaver.clients import slack_install_oauth, slack_signin_oauth
from busy_beaver.common.oauth import OAuthError
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.extensions import db
from busy_beaver.models import SlackInstallation, SlackUser

logger = logging.getLogger(__name__)

SIGN_IN_TO_SLACK = (
    "Follow the link below to access Busy Beaver settings. "
    "You will be required to sign-in with your Slack account."
)


class Output(NamedTuple):
    text: str
    url: str


####################
# Sign-in with Slack
####################
class UserDetails(NamedTuple):
    is_admin: bool
    details: tuple


def create_link_to_login_to_settings(slack_id, workspace_id):
    slack_installation = SlackInstallation.query.filter_by(
        workspace_id=workspace_id
    ).first()

    user = SlackUser.query.filter_by(
        slack_id=slack_id, installation=slack_installation
    ).first()
    if not user:
        logger.info("Creating new account.")
        user = SlackUser()
        user.slack_id = slack_id
        user.installation = slack_installation

    auth = slack_signin_oauth.generate_authentication_tuple()
    user.slack_oauth_state = auth.state
    db.session.add(user)
    db.session.commit()

    return Output(SIGN_IN_TO_SLACK, auth.url)


def process_slack_sign_in_callback(callback_url, state):
    user = SlackUser.query.filter_by(slack_oauth_state=state).first()
    if not user:
        logger.error("Sign-in with Slack state does not match")
        raise OAuthError("Sign-in with Slack failed. Please try again.")

    user_details = slack_signin_oauth.process_callback(callback_url, state)
    installation = SlackInstallation.query.filter_by(
        workspace_id=user_details.workspace_id
    ).first()
    slack = SlackClient(installation.bot_access_token)
    is_admin = slack.is_admin(user_details.user_id)

    extra = {
        "user_id": user_details.user_id,
        "workspace_id": user_details.workspace_id,
        "is_admin": is_admin,
    }
    logger.info("User logged into Busy Beaver", extra=extra)

    return UserDetails(is_admin, user_details)


##############
# Installation
##############
def process_slack_installation_callback(callback_url, state):
    """Verify callback and save tokens in the database"""
    oauth_details = slack_install_oauth.process_callback(callback_url, state)
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
