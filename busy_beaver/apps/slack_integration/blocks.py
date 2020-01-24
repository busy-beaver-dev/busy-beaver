from busy_beaver.toolbox.slack_block_kit import Divider, Section


class AppHome:
    def __init__(self):
        self.blocks = [
            Section("*Upcoming Events*"),
            Divider(),
            Section("how 2tasdfasdo use"),
        ]

    def __repr__(self):  # pragma: no cover
        return "<AppHome>"

    def __len__(self):
        return len(self.blocks)

    def __getitem__(self, i):
        return self.blocks[i]

    def to_dict(self) -> dict:
        blocks = [block.to_dict() for block in self.blocks]
        return {"type": "home", "blocks": blocks}
