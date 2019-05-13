import logging
from logging.config import dictConfig as load_dict_config
import pathlib
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from .adapters import (
    GitHubAdapter,
    KeyValueStoreAdapter,
    MeetupAdapter,
    SlackAdapter,
    TwitterAdapter,
)
from .config import (
    GITHUB_OAUTH_TOKEN,
    IN_PRODUCTION,
    LOGGING_CONFIG,
    MEETUP_API_KEY,
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
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[FlaskIntegration()])

logger.info("[BusyBeaver] Configure Integrations")
github = GitHubAdapter(GITHUB_OAUTH_TOKEN)
kv_store = KeyValueStoreAdapter()
meetup = MeetupAdapter(MEETUP_API_KEY)
slack = SlackAdapter(SLACK_TOKEN)
twitter = TwitterAdapter(
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)

logger.info("[BusyBeaver] Starting Server")
from .app import create_app  # noqa
from .models import *  # noqa
