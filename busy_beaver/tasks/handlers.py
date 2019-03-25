import logging

from busy_beaver.config import TASK_QUEUE_MAX_RETRIES
from busy_beaver.exceptions import AsyncException
from busy_beaver.extensions import db
from busy_beaver.models import Task

logger = logging.getLogger(__name__)
MAX_FAILURES = TASK_QUEUE_MAX_RETRIES + 1


def retry_failed_job(job, *exc_info):
    job.meta.setdefault("failures", 0)
    job.meta["failures"] += 1
    job.save()

    # TODO save additional information about the job here
    # maybe put into a separate queue for offline viewing?

    num_failures = job.meta["failures"]
    if num_failures >= MAX_FAILURES:
        task = Task.query.get(job.id)
        task.failed = True
        db.session.add(task)
        db.session.commit()
        raise AsyncException(f"Job failed {num_failures} times")
