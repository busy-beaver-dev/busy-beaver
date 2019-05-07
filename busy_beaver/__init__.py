import logging
from logging.config import dictConfig as load_dict_config
import pathlib
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from .adapters import GitHubAdapter, KeyValueStoreAdapter, SlackAdapter, TwitterAdapter
from .config import IN_PRODUCTION, config

# Forgot why I do this... probalby should have commented as it is not ovious
# TODO test if it is needed in datadog
pathlib.Path("logs").mkdir(exist_ok=True)

# observability
load_dict_config(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)
if IN_PRODUCTION and config.SENTRY_DSN:
    sentry_sdk.init(dsn=config.SENTRY_DSN, integrations=[FlaskIntegration()])

logger.info("[BusyBeaver] Configure Integrations")
github = GitHubAdapter(config.GITHUB_OAUTH_TOKEN)
kv_store = KeyValueStoreAdapter()
slack = SlackAdapter(config.SLACK_TOKEN)
twitter = TwitterAdapter(
    config.TWITTER_CONSUMER_KEY,
    config.TWITTER_CONSUMER_SECRET,
    config.TWITTER_ACCESS_TOKEN,
    config.TWITTER_ACCESS_TOKEN_SECRET,
)

logger.info("[BusyBeaver] Starting Server")
from .app import create_app  # noqa
from .models import *  # noqa
