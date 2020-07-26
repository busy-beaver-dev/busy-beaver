import logging

from busy_beaver.common.wrappers import SlackClient
from busy_beaver.extensions import db
from busy_beaver.models import UpcomingEventsConfiguration

logger = logging.getLogger(__name__)


# TODO need to update
ACTIVE_MESSAGE = (
    "Confirmed; I will post daily summaries at {time}.\n\n"
    "GitHub Summary feature is active! :tada: \n\n"
    "You can use the following text to publicize the bot:\n"
    "> Busy Beaver is a community engagement bot that shares daily "
    "sumarries of public GitHub activity for registered users. "
    "Find out what everybody's working on in <#{channel}>!"
)


def create_or_update_upcoming_events_configuration(
    installation,
    channel,
    post_day_of_week,
    post_time,
    post_timezone,
    post_num_events,
    slack_id,
):
    config = installation.upcoming_events_config
    if config is None:
        config = UpcomingEventsConfiguration()
        config.slack_installation = installation
        config.enabled = True
    config.channel = channel
    config.post_day_of_week = post_day_of_week
    config.post_time = post_time
    config.post_timezone = post_timezone
    config.post_num_events = post_num_events
    db.session.add(config)
    db.session.commit()

    channel = config.channel
    slack = SlackClient(installation.bot_access_token)
    slack.dm(
        ACTIVE_MESSAGE.format(time=str(post_time), channel=channel), user_id=slack_id
    )
