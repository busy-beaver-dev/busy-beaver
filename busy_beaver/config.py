import os

IN_PRODUCTION = os.getenv("IN_PRODUCTION", False)
SENTRY_ENV_FILTER = "production" if IN_PRODUCTION else "staging"
TASK_QUEUE_MAX_RETRIES = 1

SECRET_KEY = os.getenv("SECRET_KEY", "abcdef").encode("utf-8")

BASE_URL = os.getenv("BASE_URL")

# infrastructure
DATABASE_URI = os.getenv("DATABASE_URI")
REDIS_URI = os.getenv("REDIS_URI")

# social media details
TWITTER_USERNAME = "ChicagoPython"
YOUTUBE_CHANNEL = "UCT372EAC1orBOSUd2fsA8WA"

SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID", None)
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET", None)
SLACK_TOKEN = os.getenv("SLACK_BOTUSER_OAUTH_TOKEN", None)
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "TestSigningSecretSlack")

# credentials
GITHUB_OAUTH_TOKEN = os.getenv("GITHUB_OAUTH_TOKEN", None)
GITHUB_CLIENT_ID = os.getenv("GITHUB_APP_CLIENT_ID", None)
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_APP_CLIENT_SECRET", None)
GITHUB_SIGNING_SECRET = os.getenv("GITHUB_SIGNING_SECRET", "TestSigningSecretGitHub")

MEETUP_API_KEY = os.getenv("MEETUP_API_KEY", "abcdef")

TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY", None)
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET", None)
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", None)
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", None)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", None)

DIGITALOCEAN_SPACES_KEY = os.getenv("DIGITALOCEAN_SPACES_KEY", None)
DIGITALOCEAN_SPACES_SECRET = os.getenv("DIGITALOCEAN_SPACES_SECRET", None)
DIGITALOCEAN_SPACES_ENDPOINT_URL = os.getenv("DIGITALOCEAN_SPACES_ENDPOINT_URL", None)
DIGITALOCEAN_SPACES_REGION_NAME = os.getenv("DIGITALOCEAN_SPACES_REGION_NAME", None)

# observability
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s %(name)s:%(lineno)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(filename)s %(funcName)s %(lineno)s %(message)s",  # noqa
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
        "console_json": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    "loggers": {
        "busy_beaver": {
            "handlers": ["console_json"] if IN_PRODUCTION else ["console"],
            "level": "INFO" if IN_PRODUCTION else "DEBUG",
        }
    },
}
SENTRY_DSN = os.getenv("SENTRY_DSN", None)
