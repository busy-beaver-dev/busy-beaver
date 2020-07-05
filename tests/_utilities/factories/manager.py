from .event import Event
from .event_details import EventDetails
from .github_summary_user import GitHubSummaryConfiguration, GitHubSummaryUser
from .slack import SlackInstallation, SlackUser
from .tweet import Tweet


class FactoryManager:
    known_factories = [
        Event,
        EventDetails,
        GitHubSummaryConfiguration,
        GitHubSummaryUser,
        SlackInstallation,
        SlackUser,
        Tweet,
    ]

    def __init__(self, session):
        self.session = session

        for factory_func in self.known_factories:
            setattr(self, factory_func.__name__, factory_func(self.session))
