from .event import EventFactory
from .event_details import EventDetailsFactory
from .slack import SlackInstallationFactory


class FactoryManager:
    known_factories = [EventFactory, EventDetailsFactory, SlackInstallationFactory]

    def __init__(self, session):
        self.session = session

        for factory_func in self.known_factories:
            setattr(self, factory_func.__name__, factory_func(self.session))
