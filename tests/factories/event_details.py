from datetime import datetime, timedelta
import factory
from busy_beaver.adapters.meetup import EventDetails


def EventDetailsFactory(session):
    class _EventDetailsFactory(factory.Factory):
        class Meta:
            model = EventDetails

        id = factory.Faker("uuid4")
        name = "ChiPy"
        url = "http://meetup.com/_ChiPy_/event/blah"
        start_epoch = int((datetime.now() + timedelta(days=1)).timestamp())
        end_epoch = start_epoch + 60 * 60 * 2
        venue = "Numerator"

    return _EventDetailsFactory
