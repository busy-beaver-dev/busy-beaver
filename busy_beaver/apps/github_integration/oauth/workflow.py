import logging
from typing import NamedTuple

from busy_beaver.clients import github_oauth
from busy_beaver.common.oauth import OAuthError
from busy_beaver.extensions import db
from busy_beaver.models import GitHubSummaryUser

logger = logging.getLogger(__name__)


ACCOUNT_ALREADY_ASSOCIATED = (
    "You have already associated a GitHub account with your Slack handle. "
    "Please use `/busybeaver reconnect` to link to a different account."
)
VERIFY_ACCOUNT = (
    "Follow the link below to validate your GitHub account. "
    "I'll reference your GitHub username to track your public activity."
)


class Output(NamedTuple):
    text: str
    url: str


def connect_github_to_slack(slack_installation, slack_user):
    user_record = GitHubSummaryUser.query.filter_by(
        slack_id=slack_user.slack_id,
        config_id=slack_installation.github_summary_config.id,
    ).first()
    if user_record:
        logger.info("GitHub account already linked")
        return Output(ACCOUNT_ALREADY_ASSOCIATED, "")

    logger.info("Creating new account. Attemping GitHub link")
    user = GitHubSummaryUser()
    user.slack_id = slack_user.slack_id
    user.config_id = slack_installation.github_summary_config.id

    auth = github_oauth.generate_authentication_tuple()
    user.github_state = auth.state
    db.session.add(user)
    db.session.commit()

    return Output(VERIFY_ACCOUNT, auth.url)


def relink_github_to_slack(slack_installation, slack_user):
    user = GitHubSummaryUser.query.filter_by(
        slack_id=slack_user.slack_id,
        config_id=slack_installation.github_summary_config.id,
    ).first()
    if not user:
        logger.info("User has not registered before; kick off a new connect")
        return connect_github_to_slack(slack_installation, slack_user)

    auth = github_oauth.generate_authentication_tuple()
    user.github_state = auth.state
    db.session.add(user)
    db.session.commit()
    return Output(VERIFY_ACCOUNT, auth.url)


def disconnect_github_from_slack(slack_installation, slack_user):
    user = GitHubSummaryUser.query.filter_by(
        slack_id=slack_user.slack_id,
        config_id=slack_installation.github_summary_config.id,
    ).first()
    if not user:
        logger.info("Slack acount does not have associated GitHub")
        return Output("No GitHub account associated with profile", "")

    db.session.delete(user)
    db.session.commit()
    return Output("Account has been deleted. `/busybeaver connect` to reconnect", "")


def process_github_oauth_callback(callback_url, state, code):
    user = GitHubSummaryUser.query.filter_by(github_state=state).first()
    if not user:
        logger.error("GitHub state does not match")
        raise OAuthError("GitHub verification failed. Please try again.")

    oauth_details = github_oauth.process_callback(callback_url)
    _save_github_user_information_to_database(user, oauth_details)

    logger.info("Account is linked to GitHub")
    return {"Login": "successful"}


def _save_github_user_information_to_database(user, oauth_details):
    user.github_id = oauth_details.github_id
    user.github_username = oauth_details.github_username
    user.github_state = None
    user.github_access_token = oauth_details.access_token

    db.session.add(user)
    db.session.commit()
