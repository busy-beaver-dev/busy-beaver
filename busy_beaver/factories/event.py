import uuid
import factory

from busy_beaver.extensions import db
from busy_beaver.models import Event


class EventFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Event
        sqlalchemy_session = db.session

    remote_id = str(uuid.uuid4())
    name = "ChiPy"
    url = "http://meetup.com/_ChiPy_/event/blah"
    utc_epoch = 1_557_959_400_000
    venue = "Numerator"
