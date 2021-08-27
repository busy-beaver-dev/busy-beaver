from datetime import datetime
import logging

from busy_beaver.toolbox.slack_block_kit import Divider, Section
from busy_beaver.toolbox.slack_block_kit.elements import Image

logger = logging.getLogger(__name__)


class GitHubSummaryPost:
    def __init__(self, all_user_events):
        self.all_user_events = all_user_events

    def __repr__(self):  # pragma: no cover
        return "<GitHubSummaryPost>"

    def as_blocks(self):
        output = [
            Section(f"*Daily GitHub Summary -- {datetime.now():%B %d, %Y}*"),
            Divider(),
        ]

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
