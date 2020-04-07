import logging
from logging.config import dictConfig as load_dict_config

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .config import LOGGING_CONFIG, SENTRY_DSN, SENTRY_ENV_FILTER

# observability
load_dict_config(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENV_FILTER,
        integrations=[FlaskIntegration(), SqlalchemyIntegration()],
    )

logger.info("[BusyBeaver] Configure Integrations")
from . import clients  # noqa isort:skip

logger.info("[BusyBeaver] Starting Server")
from .app import create_app  # noqa isort:skip
from . import models  # noqa isort:skip
