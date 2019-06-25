from .event import Event
from .event_details import EventDetails
from .slack import SlackInstallation
from .tweet import Tweet
from .user import ApiUser, GitHubSummaryUser


class FactoryManager:
    known_factories = [
        ApiUser,
        Event,
        EventDetails,
        GitHubSummaryUser,
        SlackInstallation,
        Tweet,
    ]

    def __init__(self, session):
        self.session = session

        for factory_func in self.known_factories:
            setattr(self, factory_func.__name__, factory_func(self.session))
