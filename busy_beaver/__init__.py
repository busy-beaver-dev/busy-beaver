import logging
from logging.config import dictConfig as load_dict_config
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .config import IN_PRODUCTION, LOGGING_CONFIG, SENTRY_DSN

# observability
load_dict_config(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
if IN_PRODUCTION and SENTRY_DSN:
    integrations = [FlaskIntegration(), SqlalchemyIntegration()]
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=integrations)

logger.info("[BusyBeaver] Configure Integrations")
from . import clients  # noqa

logger.info("[BusyBeaver] Starting Server")
from .app import create_app  # noqa
from . import models  # noqa
