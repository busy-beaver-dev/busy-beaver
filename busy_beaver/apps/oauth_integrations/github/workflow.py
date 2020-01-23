import logging

from busy_beaver.clients import github_oauth
from busy_beaver.extensions import db
from busy_beaver.models import GitHubSummaryUser

logger = logging.getLogger(__name__)


def generate_github_auth_url(user: GitHubSummaryUser) -> str:
    auth = github_oauth.generate_authentication_tuple()

    user.github_state = auth.state
    db.session.add(user)
    db.session.commit()

    return auth.url


def process_github_oauth_callback(callback_url, state, code):
    user = GitHubSummaryUser.query.filter_by(github_state=state).first()
    if not user:
        logger.error("GitHub state does not match")
        return {"Message": "Please reach out for help in the #busy-beaver channel"}

    oauth_details = github_oauth.process_callback(callback_url, state)
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
