from typing import List

from busy_beaver.common.wrappers.meetup import EventDetails
from busy_beaver.toolbox.slack_block_kit import Context, Divider, Image, Section


class UpcomingEventList:
    def __init__(self, events: List[EventDetails], image_url: str):
        output = [
            Image(image_url=image_url, alt_text="Logo"),
            Section("*Upcoming Events*"),
            Divider(),
        ]

        if len(events) == 0:
            output.append(Section("No events scheduled"))

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
            f"<!date^{event.start_epoch}^{{date_long}} @ {{time}}|no date>"
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
