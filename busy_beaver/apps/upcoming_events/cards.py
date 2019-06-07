from typing import List

from busy_beaver.adapters.meetup import EventDetails
from busy_beaver.toolbox.slack_block_kit import Context, Divider, Image, Section


class UpcomingEventList:
    def __init__(self, events: List[EventDetails], group_name: str, image_url: str):
        # TODO when we go multitenant, the image box will need to change
        output = [
            Image(image_url=image_url, alt_text=group_name),
            Section("*Upcoming Events*"),
            Divider(),
        ]

        for event_details in events:
            output.extend(UpcomingEvent(event_details))

        self.output = output

    def __repr__(self):  # pragma: no cover
        return "<UpcomingEventList>"

    def __len__(self):
        return len(self.output)

    def __getitem__(self, i):
        return self.output[i]

    def to_dict(self) -> dict:
        return [block.to_dict() for block in self.output]


class UpcomingEvent:
    def __init__(self, event: EventDetails):
        event_information_string = (
            f"*<{event.url}|{event.name}>*\n"
            f"<!date^{event.dt}^{{date_long}} @ {{time}}|no date>"
        )
        event_location_string = f":round_pushpin: Location: {event.venue}"
        self.output = [
            Section(text=event_information_string),
            Context(text=event_location_string),
            Divider(),
        ]

    def __repr__(self):  # pragma: no cover
        return "<UpcomingEvent>"

    def __len__(self):
        return len(self.output)

    def __getitem__(self, i):
        return self.output[i]

    def to_dict(self) -> dict:
        return [block.to_dict() for block in self.output]
