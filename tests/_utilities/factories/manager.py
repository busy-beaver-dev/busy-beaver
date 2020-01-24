from .event import Event
from .event_details import EventDetails
from .github_summary_user import GitHubSummaryConfiguration, GitHubSummaryUser
from .slack import SlackAppHomeOpened, SlackInstallation
from .tweet import Tweet
from .user import ApiUser


class FactoryManager:
    known_factories = [
        ApiUser,
        Event,
        EventDetails,
        GitHubSummaryConfiguration,
        GitHubSummaryUser,
        SlackAppHomeOpened,
        SlackInstallation,
        Tweet,
    ]

    def __init__(self, session):
        self.session = session

        for factory_func in self.known_factories:
            setattr(self, factory_func.__name__, factory_func(self.session))
