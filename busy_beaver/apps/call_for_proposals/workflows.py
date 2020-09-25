import logging

from busy_beaver.extensions import db
from busy_beaver.models import CallForProposalsConfiguration

logger = logging.getLogger(__name__)


def create_or_update_call_for_proposals_configuration(
    installation, channel, internal_cfps
):
    config = installation.cfp_config
    if config is None:
        config = CallForProposalsConfiguration()
        config.slack_installation = installation
        config.enabled = True

    config.internal_cfps = internal_cfps
    config.channel = channel
    db.session.add(config)
    db.session.commit()
