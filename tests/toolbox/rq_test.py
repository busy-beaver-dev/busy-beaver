import pytest
from rq import get_current_job

from busy_beaver.extensions import db, rq
from busy_beaver.models import Task
from busy_beaver.toolbox import set_task_progress


@rq.job
def add(x, y):
    job = get_current_job()
    task = Task(job_id=job.id, name="Test Task", description="Trying things out")
    db.session.add(task)
    db.session.commit()

    set_task_progress(100)
    return x + y


@pytest.mark.unit
def test_set_task_progress(session):
    job = add.queue(1, 2)

    curr_task = Task.query.filter_by(job_id=job.id).first()
    assert curr_task.complete is True
    assert curr_task.failed is False
