"""Tools to make it easier to work with Slack Block Kit

Block Kit is a new UI framework that offers you more control and flexibility
when building messages for Slack. Comprised of "blocks," stackable bits of message UI,
you can customize the order and appearance of information delivered by your app in Slack

- https://api.slack.com/block-kit
- https://api.slack.com/tools/block-kit-builder
"""


class Block:
    """Generic block object, serves as a base class for Slack Block Components

    Can use `block_id` to track user integration asynchronously.

    https://api.slack.com/reference/messaging/blocks
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


class Context(Block):
    """Opinionated Context block wrapper

    Displays message context, which can include both images and text.

    https://api.slack.com/reference/messaging/blocks#context
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

    https://api.slack.com/reference/messaging/blocks#divider
    """

    type = "divider"

    def __init__(self, block_id: str = ""):
        super().__init__(block_id)
        self.output["type"] = self.type


class Image(Block):
    """Opinionated Image block wrapper

    A simple image block, designed to make those cat photos really pop.

    https://api.slack.com/reference/messaging/blocks#image
    """

    type = "image"

    def __init__(self, image_url: str, alt_text: str, block_id: str = ""):
        super().__init__(block_id)
        self.output["type"] = self.type
        self.output["image_url"] = image_url
        self.output["alt_text"] = alt_text


class Section(Block):
    """Opinionated Section block wrapper

    A section is one of the most flexible blocks available - it can be used as a simple
    text block, in combination with text fields, or side-by-side with any of the
    available block elements.

    https://api.slack.com/reference/messaging/blocks#section
    """

    type = "section"

    def __init__(self, text: str, block_id: str = ""):
        super().__init__(block_id)
        self.output["type"] = self.type
        self.output["text"] = {"type": "mrkdwn", "text": text}
