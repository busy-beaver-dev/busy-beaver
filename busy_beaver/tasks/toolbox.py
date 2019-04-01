import logging
from rq import get_current_job

from busy_beaver.extensions import db
from busy_beaver.models import Task

logger = logging.getLogger(__name__)


def set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()

        if progress >= 100:
            task = Task.query.get(job.get_id())
            if task:
                task.complete = True
                db.session.commit()
