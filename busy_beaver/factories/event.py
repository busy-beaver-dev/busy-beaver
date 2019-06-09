from datetime import datetime, timedelta
import uuid

import factory

from busy_beaver.models import Event


class EventFactory(factory.Factory):
    class Meta:
        model = Event

    remote_id = str(uuid.uuid4())
    name = "ChiPy"
    url = "http://meetup.com/_ChiPy_/event/blah"
    start_epoch = int((datetime.now() + timedelta(days=1)).timestamp())
    end_epoch = start_epoch + 60 * 60 * 2
    venue = "Numerator"
