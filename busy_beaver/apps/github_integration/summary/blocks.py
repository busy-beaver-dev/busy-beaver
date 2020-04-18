from datetime import datetime
import logging
from typing import List, NamedTuple

from .summary import GitHubUserEvents
from busy_beaver.models import GitHubSummaryUser
from busy_beaver.toolbox.slack_block_kit import Divider, Section

logger = logging.getLogger(__name__)


no_activity_default = (
    '"If code falls outside version control, and no one is around to read it, '
    'does it make a sound?" - Zax Rosenberg'
)


class UserEvents(NamedTuple):
    user: GitHubSummaryUser
    events: GitHubUserEvents


class GitHubSummaryPost:
    def __init__(self, users: List[GitHubSummaryUser], boundary_dt: datetime):
        self.users = users
        self.boundary_dt = boundary_dt

    def __repr__(self):  # pragma: no cover
        return "<GitHubSummaryPost>"

    def create(self):
        all_user_events = []
        for idx, user in enumerate(self.users):
            logger.info("Compiling stats for {0}".format(user))
            user_events = GitHubUserEvents(user, self.boundary_dt)

            # does user have events?
            if len(user_events) > 0:
                all_user_events.append(UserEvents(user, user_events))

        self.all_user_events = all_user_events

    def as_blocks(self):
        output = [
            Section(f"*Daily GitHub Summary -- {self.boundary_dt:%B %d, %Y}*"),
            Divider(),
        ]

        for user, events in self.all_user_events:
            output.append(Section(text=events.generate_summary_text()))
            output.append(Divider())

        return [block.to_dict() for block in output]
