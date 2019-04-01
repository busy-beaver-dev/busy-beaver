import sys
import uuid

import pytest

from busy_beaver.config import TASK_QUEUE_MAX_RETRIES
from busy_beaver.exceptions import AsyncException
from busy_beaver.models import Task
from busy_beaver.tasks.handlers import retry_failed_job


@pytest.fixture
def generate_exc_info():
    def _wrapper(exc_type):
        try:
            raise exc_type
        except exc_type:
            return sys.exc_info()

    return _wrapper


def add(x, y):
    return x + y


@pytest.mark.unit
def test_retry_failed_job_handler_max_failures(app, rq, session, generate_exc_info):
    # create record in db
    job_id = str(uuid.uuid4())
    task = Task(job_id=job_id, name="Add", description="Add task")
    session.add(task)
    session.commit()

    # queue up job
    rq.job(add)
    job = add.queue(5, 2, job_id=job_id)

    # fail job max number of times - 1
    exc_info = generate_exc_info(ValueError)
    for _ in range(TASK_QUEUE_MAX_RETRIES):
        retry_failed_job(job, exc_info)

    with pytest.raises(AsyncException):
        retry_failed_job(job, exc_info)

    task = Task.query.filter_by(job_id=job_id).first()
    assert task.failed is True
    assert job.meta["failures"] == TASK_QUEUE_MAX_RETRIES + 1
