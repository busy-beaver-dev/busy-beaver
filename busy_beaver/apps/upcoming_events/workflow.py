import logging

from .upcoming_events import generate_upcoming_events_message
from busy_beaver.clients import SlackClient
from busy_beaver.extensions import db, rq
from busy_beaver.models import UpcomingEventsConfiguration, UpcomingEventsGroup
from busy_beaver.toolbox import set_task_progress

logger = logging.getLogger(__name__)


###################
# Updating Settings
###################
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

    # TODO let the user know what it looks like with a button that will show them


def add_new_group_to_configuration(upcoming_events_config, meetup_urlname):
    group = UpcomingEventsGroup()
    group.configuration = upcoming_events_config
    group.meetup_urlname = meetup_urlname
    db.session.add(group)
    db.session.commit()


######################
# Post Upcoming Events
######################
@rq.job
def post_upcoming_events_message(config_id: str):
    config = UpcomingEventsConfiguration.query.get(config_id)
    if not config.enabled:
        logger.warn("Upcoming Events Configuration is not enabled")
        return

    installation = config.slack_installation
    slack = SlackClient(installation.bot_access_token)

    blocks = generate_upcoming_events_message(config, config.post_num_events)
    slack.post_message(blocks=blocks, channel=config.channel)
    set_task_progress(100)
