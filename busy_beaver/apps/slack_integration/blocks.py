from busy_beaver.apps.upcoming_events.workflow import generate_upcoming_events_message
from busy_beaver.toolbox.slack_block_kit import Block, Divider, Section

APP_HOME_HEADER_INSTALLED = (
    "*Welcome!* Busy Beaver is a community engagement bot.\n\n"
    "Join <#{channel}> to see daily GitHub summaries for registered users. "
    "Wanna join the fun? `/busybeaver connect` to link your GitHub account!"
)
APP_HOME_HEADER = (
    "*Welcome!* Busy Beaver is a community engagement bot.\n\n"
    "Please contact the Slack workspace admin to complete installation."
)


class AppHome:
    def __init__(self, *, channel=None, meetup_group=None):
        if channel:
            header = APP_HOME_HEADER_INSTALLED.format(channel=channel)
        else:
            header = APP_HOME_HEADER
        blocks = [Section(header)]

        if meetup_group:
            blocks.extend([Divider(), Section("\n\n\n\n")])
            blocks.extend(generate_upcoming_events_message(meetup_group, count=5))

        self.blocks = blocks

    def __repr__(self):  # pragma: no cover
        return "<AppHome>"

    def __len__(self):
        return len(self.blocks)

    def __getitem__(self, i):
        return self.blocks[i]

    def to_dict(self) -> dict:
        blocks = [
            block.to_dict() if isinstance(block, Block) else block
            for block in self.blocks
        ]
        return {"type": "home", "blocks": blocks}
