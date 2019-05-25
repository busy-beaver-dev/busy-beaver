from typing import List

from .block_kit import Context, Divider, Section
from busy_beaver.adapters.meetup import EventDetails


class UpcomingEventList:
    def __init__(self, title, events: List[EventDetails]):
        output = [Section(title).to_dict(), Divider().to_dict()]

        for event_details in events:
            output.extend(UpcomingEvent(event_details).to_dict())

        self.output = output

    def to_dict(self) -> dict:
        return self.output


class UpcomingEvent:
    def __init__(self, event: EventDetails):
        event_information_string = (
            f"*<{event.url}|{event.name}>*\n"
            f"<!date^{event.dt}^{{time}} {{date_long}}|no date>"
        )
        event_location_string = f":round_pushpin: Location: {event.venue}"
        self.output = [
            Section(text=event_information_string).to_dict(),
            Context(text=event_location_string).to_dict(),
            Divider(event_location_string).to_dict(),
        ]

    def to_dict(self) -> dict:
        return self.output
