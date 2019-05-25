"""Creates factories to produce test data

As we are using the adapter pattern to wrap APIs, we can simplify our testing process
by creating factories to produce fixtures.
"""

import factory
from busy_beaver.adapters.meetup import EventDetails


class EventDetailsFactory(factory.Factory):
    class Meta:
        model = EventDetails

    name = "ChiPy"
    url = "http://meetup.com/_ChiPy_/event/blah"
    dt = 1_557_959_400_000
    venue = "Numerator"
