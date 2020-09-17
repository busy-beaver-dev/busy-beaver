import logging

from .upcoming_events import generate_upcoming_events_message
from busy_beaver.clients import SlackClient, meetup
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


def add_new_group_to_configuration(
    installation, upcoming_events_config, meetup_urlname
):
    group = UpcomingEventsGroup()
    group.meetup_urlname = meetup_urlname
    if not upcoming_events_config:
        config = UpcomingEventsConfiguration()
        config.slack_installation = installation
        config.enabled = True
        config.post_num_events = 1
        group.configuration = config
    else:
        group.configuration = upcoming_events_config

    db.session.add(group)
    db.session.commit()
    _add_events_to_database.queue(group.id)


@rq.job
def _add_events_to_database(group_id: int):
    group = UpcomingEventsGroup.query.get(group_id)
    events = meetup.get_events(group.meetup_urlname, count=5)

    num_created = 0
    for event in events:
        record = event.create_event_record()
        record.group = group
        db.session.add(record)
        num_created += 1
    else:
        db.session.commit()
        logger.info("{0} events saved to the database".format(num_created))


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

    blocks = generate_upcoming_events_message(config)
    slack.post_message(blocks=blocks, channel=config.channel)
    set_task_progress(100)
