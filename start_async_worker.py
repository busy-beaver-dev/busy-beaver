from logging.config import dictConfig as load_dict_config

import sentry_sdk
from sentry_sdk.integrations.rq import RqIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from busy_beaver.app import create_app
from busy_beaver.config import IN_PRODUCTION, LOGGING_CONFIG, SENTRY_DSN
from busy_beaver.extensions import rq
from busy_beaver.toolbox.rq import retry_failed_job

# observability
load_dict_config(LOGGING_CONFIG)
if IN_PRODUCTION and SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN, integrations=[RqIntegration(), SqlalchemyIntegration()])

app = create_app()
ctx = app.app_context()
ctx.push()

w = rq.get_worker("default", "failed")
w.push_exc_handler(retry_failed_job)
w.work()
