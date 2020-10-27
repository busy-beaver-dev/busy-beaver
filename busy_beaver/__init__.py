import logging
from logging.config import dictConfig as load_dict_config

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .config import ENVIRONMENT, LOGGING_CONFIG, SENTRY_DSN

# observability
load_dict_config(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        integrations=[FlaskIntegration(), SqlalchemyIntegration()],
    )

logger.info("Configure Integrations")
from . import clients  # noqa isort:skip

logger.info("Starting Server")
from .app import create_app  # noqa isort:skip
from . import models  # noqa isort:skip
