from datetime import datetime, time, timedelta

import factory

from .slack import SlackInstallation
from busy_beaver.models import Event as event_model
from busy_beaver.models import UpcomingEventsConfiguration as event_config_model
from busy_beaver.models import UpcomingEventsGroup as event_group_model


def UpcomingEventsConfiguration(session):
    class _EventFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = event_config_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        enabled = True
        slack_installation = factory.SubFactory(SlackInstallation(session))
        channel = "announcements"
        post_day_of_week = "Monday"
        post_time = time(9, 00)
        post_timezone = "America/Chicago"
        post_num_events = 3

    return _EventFactory


def UpcomingEventsGroup(session):
    class _UpcomingEventsGroupFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = event_group_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        meetup_urlname = "_ChiPy_"
        configuration = factory.SubFactory(UpcomingEventsConfiguration(session))

    return _UpcomingEventsGroupFactory


def Event(session):
    class _EventFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = event_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        remote_id = factory.Faker("uuid4")
        name = "ChiPy"
        url = "http://meetup.com/_ChiPy_/event/blah"
        start_epoch = int((datetime.now() + timedelta(days=1)).timestamp())
        end_epoch = start_epoch + 60 * 60 * 2
        venue = "Braintree"
        group = factory.SubFactory(UpcomingEventsGroup(session))

    return _EventFactory
