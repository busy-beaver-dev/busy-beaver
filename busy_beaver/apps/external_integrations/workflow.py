from .oauth_providers.base import OAuthError
from busy_beaver import slack_oauth
from busy_beaver.extensions import db
from busy_beaver.models import SlackInstallation


def slack_generate_and_save_auth_tuple():
    auth = slack_oauth.generate_authentication_tuple()
    new_installation = SlackInstallation(state=auth.state)
    db.session.add(new_installation)
    db.session.commit()
    return auth


def slack_verify_callback_and_save_access_tokens_in_database(callback_url, state):
    installation = SlackInstallation.query.filter_by(state=state).first()

    if not installation:
        raise OAuthError("state not found")
    oauth_details = slack_oauth.process_callback(callback_url, state)

    # does this exist?
    workspace_installation = SlackInstallation.query.filter_by(
        workspace_id=oauth_details.workspace_id
    ).first()
    if workspace_installation:
        installation = workspace_installation

    installation.patch(oauth_details._asdict().update({"state": ""}))
    db.session.add(installation)
    db.session.commit()
