import logging
from typing import NamedTuple

from busy_beaver.clients import slack_install_oauth, slack_signin_oauth
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.extensions import db
from busy_beaver.models import GitHubSummaryConfiguration, SlackInstallation, SlackUser

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


def create_link_to_login_to_settings(slack_user):
    auth = slack_signin_oauth.generate_authentication_tuple()
    return Output(SIGN_IN_TO_SLACK, auth.url)


def process_slack_sign_in_callback(callback_url):
    user_details = slack_signin_oauth.process_callback(callback_url)
    installation = SlackInstallation.query.filter_by(
        workspace_id=user_details.workspace_id
    ).first()
    slack_user = SlackUser.query.filter_by(
        slack_id=user_details.slack_id, installation=installation
    ).first()
    if not slack_user:
        slack_user = SlackUser()
        slack_user.slack_id = user_details.slack_id
        slack_user.installation = installation
        db.session.add(slack_user)
        db.session.commit()

    extra = {"user_id": slack_user.slack_id, "workspace_id": installation.workspace_id}
    logger.info("User logged into Busy Beaver", extra=extra)
    return slack_user


##############
# Installation
##############
def process_slack_installation_callback(callback_url):
    """Verify callback and save tokens in the database"""
    oauth_details = slack_install_oauth.process_callback(callback_url)
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
    ":zap: `/busybeaver settings` to configure Busy Beaver\n"
)


def send_welcome_message(installation: SlackInstallation):
    slack = SlackClient(installation.bot_access_token)
    user_id = installation.authorizing_user_id
    slack.dm(ONBOARDING_MESSAGE.format(slack_id=user_id), user_id=user_id)


ACTIVE_MESSAGE = (
    "Confirmed; I will post daily summaries at {time}.\n\n"
    "Busy Beaver is now active! :tada: \n\n"
    "You can use the following text to publicize the bot:\n"
    "> Busy Beaver is a community engagement bot that shares daily "
    "sumarries of public GitHub activity for registered users. "
    "Find out what everybody's working on in <#{channel}>!"
)


def create_or_update_configuration(
    installation, channel, time_to_post, timezone_to_post, slack_id
):
    config = installation.github_summary_config
    if config is None:
        config = GitHubSummaryConfiguration()
    config.channel = channel
    config.summary_post_time = time_to_post
    config.summary_post_timezone = timezone_to_post
    db.session.add(config)
    db.session.commit()

    channel = config.channel
    slack = SlackClient(installation.bot_access_token)
    slack.dm(
        ACTIVE_MESSAGE.format(time=str(time_to_post), channel=channel), user_id=slack_id
    )
