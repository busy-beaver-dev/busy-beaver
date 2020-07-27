import logging

from busy_beaver.extensions import db
from busy_beaver.models import UpcomingEventsConfiguration, UpcomingEventsGroup

logger = logging.getLogger(__name__)


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
