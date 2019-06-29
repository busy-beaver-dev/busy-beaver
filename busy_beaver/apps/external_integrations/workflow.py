from busy_beaver import slack_oauth
from busy_beaver.adapters import SlackAdapter
from busy_beaver.extensions import db
from busy_beaver.models import SlackInstallation


def perform(callback_url, state):
    install = verify_callback_and_save_tokens_in_database(callback_url, state)
    send_welcome_message(install)


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


ONBOARDING_MESSAGE = """Hi <@{slack_id}>! :wave:

I'm here to help engage tech-focused Slack communities.
Thank you for taking part in our beta program. :pray:

:zap: To get started `/invite` me to a public channel
:bulb: I recommend creating `#busy-beaver`

You can use the following text to publicize the bot:
> Busy Beaver is a community engagement bot that
> shares public GitHub activity for registered users.
> Join #busy-beaver to see what everybody is working on.
"""


def send_welcome_message(installation: SlackInstallation):
    slack = SlackAdapter(installation.bot_access_token)
    user_id = installation.authorizing_user_id
    slack.dm(user_id, message=ONBOARDING_MESSAGE.format(slack_id=user_id))
