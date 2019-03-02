import logging
from logging.config import dictConfig as load_dict_config
import pathlib
import sentry_sdk

from .adapters import GitHubAdapter, KeyValueStoreAdapter, SlackAdapter, TwitterAdapter
from .app import create_app
from .config import (
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

# Forgot why I do this... probalby should have commented as it is not ovious
# TODO test if it is needed in datadog
pathlib.Path("logs").mkdir(exist_ok=True)

# observability
load_dict_config(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
if IN_PRODUCTION and SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN)

logger.info("[BusyBeaver] Configure Integrations")
github = GitHubAdapter(GITHUB_OAUTH_TOKEN)
kv_store = KeyValueStoreAdapter()
slack = SlackAdapter(SLACK_TOKEN)
twitter = TwitterAdapter(
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)

logger.info("[BusyBeaver] Starting Server")
app = create_app()
from .models import *  # noqa
