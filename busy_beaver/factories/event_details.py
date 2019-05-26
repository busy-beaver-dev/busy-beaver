import uuid
import factory
from busy_beaver.adapters.meetup import EventDetails


class EventDetailsFactory(factory.Factory):
    class Meta:
        model = EventDetails

    id = str(uuid.uuid4())
    name = "ChiPy"
    url = "http://meetup.com/_ChiPy_/event/blah"
    dt = 1_557_959_400_000
    venue = "Numerator"
