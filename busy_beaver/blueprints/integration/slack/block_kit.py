from typing import Optional


class Block:
    """
    https://api.slack.com/reference/messaging/blocks
    """

    type = None

    def __init__(self, block_id=None):
        self.output = {}
        if block_id:
            self.output["block_id"] = block_id

    def to_dict(self) -> dict:
        return self.output


class Section(Block):
    """
    https://api.slack.com/reference/messaging/blocks#section
    """

    type = "section"

    def __init__(self, text: str, block_id: Optional[str] = None):
        super().__init__(block_id)
        self.output["type"] = self.type
        self.output["text"] = {"type": "mrkdwn", "text": text}


class Context(Block):
    """
    Displays message context, which can include both images and text.

    https://api.slack.com/reference/messaging/blocks#context
    """

    type = "context"

    def __init__(self, text: str = "", block_id: Optional[str] = None):
        super().__init__(block_id)
        self.output["type"] = self.type
        self.output["elements"] = [{"type": "plain_text", "emoji": True, "text": text}]


class Divider(Block):
    """
    https://api.slack.com/reference/messaging/blocks#divider
    """

    type = "divider"

    def __init__(self, block_id: Optional[str] = None):
        super().__init__(block_id)
        self.output["type"] = self.type
