from datetime import datetime, timedelta
import logging
from typing import List, NamedTuple

from .summary import GitHubUserEvents
from busy_beaver.models import GitHubSummaryUser
from busy_beaver.toolbox.slack_block_kit import Divider, Section
from busy_beaver.toolbox.slack_block_kit.elements import Image

logger = logging.getLogger(__name__)


class UserEvents(NamedTuple):
    user: GitHubSummaryUser
    events: GitHubUserEvents


class GitHubSummaryPost:
    def __init__(self, users: List[GitHubSummaryUser], boundary_dt: datetime):
        self.users = users
        self.boundary_dt = boundary_dt
        self.now = boundary_dt + timedelta(days=1)

    def __repr__(self):  # pragma: no cover
        return "<GitHubSummaryPost>"

    def create(self):
        all_user_events = []
        for idx, user in enumerate(self.users):
            logger.info("Compiling stats for {0}".format(user))
            user_events = GitHubUserEvents(user, self.boundary_dt)

            if len(user_events) > 0:
                all_user_events.append(UserEvents(user, user_events))

        self.all_user_events = all_user_events

    def as_blocks(self):
        output = [Section(f"*Daily GitHub Summary -- {self.now:%B %d, %Y}*"), Divider()]

        if not self.all_user_events:
            output.append(Section(text="No activity to report."))
            output.append(Divider())
            return [block.to_dict() for block in output]

        for user, events in self.all_user_events:
            profile_pic = (
                f"https://avatars.githubusercontent.com/u/{user.github_id}?size=75"
            )
            img = Image(image_url=profile_pic, alt_text=f"{user.github_username}")
            output.append(Section(text=events.generate_summary_text(), accessory=img))
            output.append(Divider())
        return [block.to_dict() for block in output]
