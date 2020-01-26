from datetime import datetime, timedelta

import factory

from busy_beaver.models import Event as model


def Event(session):
    class _EventFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        remote_id = factory.Faker("uuid4")
        name = "ChiPy"
        url = "http://meetup.com/_ChiPy_/event/blah"
        start_epoch = int((datetime.now() + timedelta(days=1)).timestamp())
        end_epoch = start_epoch + 60 * 60 * 2
        venue = "Numerator"

    return _EventFactory
