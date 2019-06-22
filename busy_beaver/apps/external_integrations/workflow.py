from busy_beaver import slack_oauth
from busy_beaver.extensions import db
from busy_beaver.models import SlackInstallation


def slack_verify_callback_and_save_access_tokens_in_database(callback_url, state):
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
