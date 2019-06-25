from .event import EventFactory
from .event_details import EventDetailsFactory
from .slack import SlackInstallationFactory
from .tweet import TweetFactory


class FactoryManager:
    known_factories = [
        EventFactory,
        EventDetailsFactory,
        SlackInstallationFactory,
        TweetFactory,
    ]

    def __init__(self, session):
        self.session = session

        for factory_func in self.known_factories:
            setattr(self, factory_func.__name__, factory_func(self.session))
