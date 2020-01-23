import logging
from logging.config import dictConfig as load_dict_config
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .adapters import SlackAdapter
from .apps.external_integrations.oauth_providers.slack import SlackOAuthFlow
from .config import (
    IN_PRODUCTION,
    LOGGING_CONFIG,
    SENTRY_DSN,
    SLACK_TOKEN,
    SLACK_CLIENT_ID,
    SLACK_CLIENT_SECRET,
)

# observability
load_dict_config(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
if IN_PRODUCTION and SENTRY_DSN:
    integrations = [FlaskIntegration(), SqlalchemyIntegration()]
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=integrations)

logger.info("[BusyBeaver] Configure Integrations")
chipy_slack = SlackAdapter(SLACK_TOKEN)  # Default Workspace -- this is being phased out
from .clients import kv_store, meetup, twitter  # noqa

slack_oauth = SlackOAuthFlow(SLACK_CLIENT_ID, SLACK_CLIENT_SECRET)

logger.info("[BusyBeaver] Starting Server")
from .app import create_app  # noqa
from .models import *  # noqa
