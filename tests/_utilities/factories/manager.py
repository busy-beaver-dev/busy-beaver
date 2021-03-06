from .cfps import CallForProposalsConfiguration
from .event import Event, UpcomingEventsConfiguration, UpcomingEventsGroup
from .event_details import EventDetails
from .github_summary_user import GitHubSummaryConfiguration, GitHubSummaryUser
from .slack import SlackInstallation, SlackUser


class FactoryManager:
    known_factories = [
        CallForProposalsConfiguration,
        Event,
        EventDetails,
        GitHubSummaryConfiguration,
        GitHubSummaryUser,
        SlackInstallation,
        SlackUser,
        UpcomingEventsConfiguration,
        UpcomingEventsGroup,
    ]

    def __init__(self, session):
        self.session = session

        for factory_func in self.known_factories:
            setattr(self, factory_func.__name__, factory_func(self.session))
