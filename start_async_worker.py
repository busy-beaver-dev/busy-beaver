from logging.config import dictConfig as load_dict_config

import sentry_sdk
from sentry_sdk.integrations.rq import RqIntegration

from busy_beaver.app import create_app
from busy_beaver.config import IN_PRODUCTION, LOGGING_CONFIG, SENTRY_DSN
from busy_beaver.extensions import rq

# observability
LOGGING_CONFIG["handlers"]["datadog_file"]["filename"] = "logs/busy_beaver_worker.json"
load_dict_config(LOGGING_CONFIG)
if IN_PRODUCTION and SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN, integrations=[RqIntegration()])

app = create_app()
ctx = app.app_context()
ctx.push()

w = rq.get_worker("default", "failed")
w.work()
