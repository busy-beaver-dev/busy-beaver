import logging

from rq import get_current_job

from busy_beaver.config import TASK_QUEUE_MAX_RETRIES
from busy_beaver.exceptions import AsyncException
from busy_beaver.extensions import db
from busy_beaver.models import Task

logger = logging.getLogger(__name__)
MAX_FAILURES = TASK_QUEUE_MAX_RETRIES + 1


def set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()

        if progress >= 100:
            task = Task.query.filter_by(job_id=job.get_id()).first()
            if task:
                task.complete = True
                db.session.commit()


def retry_failed_job(job, *exc_info):
    job.meta.setdefault("failures", 0)
    job.meta["failures"] += 1
    job.save()

    # TODO save additional information about the job here
    # maybe put into a separate queue for offline viewing?
    # if a result needs to be save, make sure we save it

    num_failures = job.meta["failures"]
    if num_failures >= MAX_FAILURES:
        task = Task.query.filter_by(job_id=job.id).first()
        # TODO update this
        task.failed = True
        db.session.add(task)
        db.session.commit()
        raise AsyncException(f"Job failed {num_failures} times")
