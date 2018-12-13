import logging
import logging.config
import pathlib

import responder
import sentry_sdk
from sqlalchemy_wrapper import SQLAlchemy

from .config import DATABASE_URI, IN_PRODUCTION, LOGGING_CONFIG, SENTRY_DSN

pathlib.Path('logs').mkdir(exist_ok=True)

# observability
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
if IN_PRODUCTION and SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN)

# web app
logger.info("[BusyBeaver] Starting Server")
api = responder.API()
db = SQLAlchemy(DATABASE_URI)
from . import models  # noqa
from . import backend  # noqa
