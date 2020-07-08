from logging.config import dictConfig as load_dict_config

import sentry_sdk
from sentry_sdk.integrations.rq import RqIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from busy_beaver.app import create_app
from busy_beaver.config import LOGGING_CONFIG, SENTRY_DSN, SENTRY_ENV_FILTER
from busy_beaver.extensions import rq
from busy_beaver.toolbox.rq import retry_failed_job

# observability
load_dict_config(LOGGING_CONFIG)
if SENTRY_DSN:
    sentry_sdk.init(
        SENTRY_DSN,
        environment=SENTRY_ENV_FILTER,
        integrations=[RqIntegration(), SqlalchemyIntegration()],
    )

app = create_app()
ctx = app.app_context()
ctx.push()

w = rq.get_worker("default", "failed")
w.push_exc_handler(retry_failed_job)
w.work()
