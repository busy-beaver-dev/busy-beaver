"""Tools to make it easier to work with Slack Block Kit

Block Kit is a new UI framework that offers you more control and flexibility
when building messages for Slack. Comprised of "blocks," stackable bits of message UI,
you can customize the order and appearance of information delivered by your app in Slack

- https://api.slack.com/block-kit
- https://api.slack.com/tools/block-kit-builder
"""
from .elements import Element


class Block:
    """Generic block object, serves as a base class for Slack Block Components

    Can use `block_id` to track user integration asynchronously.

    https://api.slack.com/reference/block-kit/blocks
    """

    type = None

    def __init__(self, block_id: str = ""):
        self.output = {}
        if block_id:
            self.output["block_id"] = block_id

    def __repr__(self):  # pragma: no cover
        cls_name = self.__class__.__name__
        return f"<{cls_name}>"

    def to_dict(self) -> dict:
        return self.output


class Action(Block):
    """Opinionated Divider block wrapper

    A content divider, like an <hr>, to split up different blocks inside of a message.
    The divider block is nice and neat, requiring only a type.

    https://api.slack.com/reference/block-kit/blocks#actions
    """

    type = "action"

    def __init__(self, block_id: str = ""):
        raise NotImplementedError


class Context(Block):
    """Opinionated Context block wrapper

    Displays message context, which can include both images and text.

    https://api.slack.com/reference/block-kit/blocks#context
    """

    type = "context"

    def __init__(self, text: str = "", block_id: str = ""):
        super().__init__(block_id)
        self.output["type"] = self.type
        self.output["elements"] = [{"type": "plain_text", "emoji": True, "text": text}]


class Divider(Block):
    """Opinionated Divider block wrapper

    A content divider, like an <hr>, to split up different blocks inside of a message.
    The divider block is nice and neat, requiring only a type.

    https://api.slack.com/reference/block-kit/blocks#divider
    """

    type = "divider"

    def __init__(self, block_id: str = ""):
        super().__init__(block_id)
        self.output["type"] = self.type


class File(Block):
    """Opinionated Image block wrapper

    Displays a remote file.

    https://api.slack.com/reference/block-kit/blocks#file
    """

    type = "file"

    def __init__(self, external_id: str, block_id: str = ""):
        self.output["type"] = self.type
        self.output["external_id"] = external_id
        self.output["source"] = "remote"


class Image(Block):
    """Opinionated Image block wrapper

    A simple image block, designed to make those cat photos really pop.

    https://api.slack.com/reference/block-kit/blocks#image
    """

    type = "image"

    def __init__(self, image_url: str, alt_text: str, block_id: str = ""):
        super().__init__(block_id)
        self.output["type"] = self.type
        self.output["image_url"] = image_url
        self.output["alt_text"] = alt_text


class Input(Block):
    """Opinionated Image block wrapper

    A block that collects information from users - it can hold a plain-text input
    element, a select menu element, a multi-select menu element, or a datepicker.

    https://api.slack.com/reference/block-kit/blocks#file
    """

    type = "input"

    def __init__(self, block_id: str = ""):
        raise NotImplementedError


class Section(Block):
    """Opinionated Section block wrapper

    A section is one of the most flexible blocks available - it can be used as a simple
    text block, in combination with text fields, or side-by-side with any of the
    available block elements.

    https://api.slack.com/reference/block-kit/blocks#section
    """

    type = "section"

    def __init__(self, text: str, *, block_id: str = "", accessory: Element = None):
        super().__init__(block_id)
        self.output["type"] = self.type
        self.output["text"] = {"type": "mrkdwn", "text": text}

        if accessory:
            self.output["accessory"] = accessory.to_dict()
