from datetime import date
import logging
from typing import NamedTuple

from dateutil.parser import parse as parse_dt
import requests

from .blueprint import cfps_bp
from .models import CallForProposalsConfiguration
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.toolbox.slack_block_kit import ContextMarkdown, Section

logger = logging.getLogger(__name__)


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


CONFERENCE_TEMPLATE = "*{cfp_end_date}*  |  <{url}|{name}>"
INTERNAL_CFP_TEMPLATE = "<{url}|{event}>"


class OpenCFPPost:
    def __init__(self, conference_cfps, internal_cfps):
        self.conference_cfp_text = self._generate_conference_text(conference_cfps)
        self.internal_cfp_text = self._generate_internal_cfp_text(internal_cfps)

    @staticmethod
    def _generate_conference_text(conference_cfps):
        output = []
        for cfp in conference_cfps:
            line = CONFERENCE_TEMPLATE.format(**cfp._asdict())
            output.append(line)
        return "\n".join(output)

    @staticmethod
    def _generate_internal_cfp_text(internal_cfps):
        output = []
        for cfp in internal_cfps:
            line = INTERNAL_CFP_TEMPLATE.format(**cfp)
            output.append(line)
        return "\n".join(output)

    def as_blocks(self):
        output = [
            Section(text=":calendar:  |  *Upcoming Deadlines*  |  :calendar:"),
            Section(text="*Conferences*"),
            ContextMarkdown(text=self.conference_cfp_text),
            Section(text="*Internal CFPs*"),
            ContextMarkdown(text=self.internal_cfp_text),
        ]
        return [block.to_dict() for block in output]


@cfps_bp.cli.command(
    "post_upcoming_cfps",
    help="Post upcoming Call-For-Proposals in all workspaces where feature is enabled",
)
def post_upcoming_cfps():
    all_active_configs = CallForProposalsConfiguration.query.filter_by(enabled=True)

    for config in all_active_configs:
        cfps = get_open_cfps()
        output_blocks = OpenCFPPost(cfps, config.internal_cfps).as_blocks()

        installation = config.slack_installation
        slack = SlackClient(installation.bot_access_token)
        slack.post_message(blocks=output_blocks, channel=config.channel)
