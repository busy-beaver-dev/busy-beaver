"""Redis & python-rq related tests"""

import pytest

from busy_beaver.extensions import rq
from busy_beaver.models import Task
from busy_beaver.tasks.toolbox import _set_task_progress


@rq.job
def add(x, y):
    return x + y


@rq.job
def add_create_task_set_job_progress(x, y):
    _set_task_progress(100)
    return x + y


@pytest.mark.smoke
def test_redis_smoke_test():
    default_queue = rq.get_queue("default")
    default_queue.get_jobs()

    assert True


def test_add(app):
    assert add(5, 2) == 7


def test_run_async_task(app):
    job = add.queue(5, 2)

    assert job.result == 7


def test_run_async_task_update_progress(app, session):
    job = add_create_task_set_job_progress.queue(5, 2)

    queued_task = Task(id=job.id, name="Add", description="Add task")
    session.add(queued_task)
    session.commit()

    queued_task.get_rq_job

    assert job.result == 7
    assert queued_task.id == job.id
    assert queued_task.get_progress() == 100
