"""
Slack Block Kit: Block Elements

Block elements can be used inside of section, context, and actions
layout blocks. Inputs can only be used inside of input blocks.

https://api.slack.com/reference/block-kit/block-elements
"""


class Element:
    type = None

    def __init__(self):
        self.output = {}
        self.output["type"] = self.type

    def __repr__(self):  # pragma: no cover
        cls_name = self.__class__.__name__
        return f"<{cls_name}>"

    def to_dict(self) -> dict:
        return self.output


class Image(Element):
    type = "image"

    def __init__(self, image_url, alt_text):
        super().__init__()
        self.output["image_url"] = image_url
        self.output["alt_text"] = alt_text


class Mrkdwn(Element):
    type = "mrkdwn"

    def __init__(self, text):
        super().__init__()
        self.output["text"] = text
        self.output["emoji"] = False
        self.output["verbatim"] = False
