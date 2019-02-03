import logging
import logging.config
import pathlib

import responder
import sentry_sdk
from sqlalchemy_wrapper import SQLAlchemy

from .config import (
    DATABASE_URI,
    GITHUB_OAUTH_TOKEN,
    IN_PRODUCTION,
    LOGGING_CONFIG,
    SENTRY_DSN,
    SLACK_TOKEN,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
)
from .adapters import GitHubAdapter, KeyValueStore, SlackAdapter, TwitterAdapter

pathlib.Path("logs").mkdir(exist_ok=True)

# observability
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
if IN_PRODUCTION and SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN)

github = GitHubAdapter(GITHUB_OAUTH_TOKEN)
slack = SlackAdapter(SLACK_TOKEN)
twitter = TwitterAdapter(
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)

# web app
logger.info("[BusyBeaver] Starting Server")
api = responder.API()
db = SQLAlchemy(DATABASE_URI)
from . import models  # noqa
kv_store = KeyValueStore(models.store)
from . import backend  # noqa
