import os

IN_PRODUCTION = os.getenv("ENV_NAME", False)

# infrastructure
local_db = "sqlite:///busy_beaver.db"
DATABASE_URI = os.getenv("DATABASE_URI", local_db)

# credentials
oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")

# observability
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(name)s:%(lineno)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(lineno)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
        "datadog_file": {
            "class": "logging.FileHandler",
            "filename": "busy_beaver_log.json",
            "mode": "w",
            "formatter": "json",
        },
    },
    "loggers": {
        "busy_beaver": {
            "handlers": ["console", "datadog_file"],
            "level": "INFO" if IN_PRODUCTION else "DEBUG",
        }
    },
}
SENTRY_DSN = os.getenv("SENTRY_DSN", None)
