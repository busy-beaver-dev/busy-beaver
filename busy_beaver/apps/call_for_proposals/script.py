from datetime import date
from typing import NamedTuple

from dateutil.parser import parse as parse_dt
import requests

from busy_beaver.toolbox.slack_block_kit import Context, Section


class Conference(NamedTuple):
    name: str
    url: str
    cfp_end_date: date


def get_open_cfps():
    r = requests.get(
        "https://raw.githubusercontent.com/vinayak-mehta/conrad/master/data/events.json"
    )
    events = r.json()

    return [
        Conference(
            name=event["name"],
            url=event["url"],
            cfp_end_date=parse_dt(event["cfp_end_date"]).date(),
        )
        for event in events
        if event["cfp_open"]
    ]


class OpenCFPPost:
    def __init__(self, conferences, ongoing):
        self.conferences = conferences
        self.ongoing = ongoing

    def as_blocks(self):
        output = [
            Section(text=":calendar:  |  *Upcoming Deadlines*  |  :calendar:"),
            Section(text="*Conferences*"),
            Context(text="\n".join(self.conferences)),
            Section(text="*Ongoing*"),
            Context(text="\n".join(self.ongoing)),
        ]
        return [block.to_dict() for block in output]


if __name__ == "__main__":
    conference_line = "*{cfp_end_date}*  |  <{url}|{name}>"
    ongoing_line = "<{url}|{name}>"
    cfps = get_open_cfps()

    conference_output = []
    for cfp in cfps:
        line = conference_line.format(**cfp._asdict())
        conference_output.append(line)

    # TODO get this out of JSON
    ongoing_output = []
    for name, url in [
        ("ChiPy `__main__` Meeting", "http://bit.ly/chipy-cfp"),
        ("Special Interest Group Events", "http://bit.ly/chipy-sig-cfp"),
    ]:
        line = ongoing_line.format(name=name, url=url)
        ongoing_output.append(line)

    output = OpenCFPPost(conference_output, ongoing_output).as_blocks()
