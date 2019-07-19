import logging
import uuid
from urllib.parse import urlencode

from busy_beaver.config import GITHUB_CLIENT_ID, GITHUB_REDIRECT_URI, MEETUP_GROUP_NAME
from busy_beaver.extensions import db
from busy_beaver.models import User
from busy_beaver.toolbox import EventEmitter

logger = logging.getLogger(__name__)
slash_command_dispatcher = EventEmitter()


ACCOUNT_ALREADY_ASSOCIATED = (
    "You have already associated a GitHub account with your Slack handle. "
    "Please use `/busybeaver reconnect` to link to a different account."
)
NO_ASSOCIATED_ACCOUNT = (
    "No associated account. Use `/busybeaver connect` to link your account."
)
VERIFY_ACCOUNT = (
    "Follow the link below to validate your GitHub account. "
    "I'll reference your GitHub username to track your public activity."
)


def add_tracking_identifer_and_save_record(user: User) -> None:
    user.github_state = str(uuid.uuid4())  # generate unique identifer to track user
    db.session.add(user)
    db.session.commit()
    return user


def create_github_account_attachment(state):
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "state": state,
    }
    query_params = urlencode(data)
    url = f"https://github.com/login/oauth/authorize?{query_params}"
    return {
        "fallback": url,
        "attachment_type": "default",
        "actions": [{"text": "Associate GitHub Profile", "type": "button", "url": url}],
    }
##########################################
# Associate GitHub account with Slack user
# TODO refactor this
##########################################
def check_account_existing(slack_id):
    user_record = User.query.filter_by(slack_id=slack_id).first()
    if user_record:
        logger.info("[Busy Beaver] Slack account already linked to Github")
        return ACCOUNT_ALREADY_ASSOCIATED
    logger.info("[Busy Beaver] New user. Linking GitHub account.")
    return NO_ASSOCIATED_ACCOUNT


def generate_account_attachment(**data):
    slack_id = data["user_id"]
    account_exists = check_account_existing(slack_id)
    if(account_exists == NO_ASSOCIATED_ACCOUNT):
        user = User()
        user.slack_id = slack_id
        user = add_tracking_identifer_and_save_record(user)
        attachment = create_github_account_attachment(user.github_state)
        return VERIFY_ACCOUNT, attachment
    return ACCOUNT_ALREADY_ASSOCIATED

