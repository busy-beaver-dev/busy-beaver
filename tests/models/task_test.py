from busy_beaver.models import Task


def test_create_task(session):
    task = Task(
        id="abcd",
        name="task_created_for_test",
        description="Task created for testing purposes",
    )

    session.add(task)
    session.commit()

    assert task.id == "abcd"
    assert task.complete is False
    assert task.failed is False


def add(x, y):
    return x + y


def test_run_async_task_update_progress(app, rq, session):
    rq.job(add)
    job = add.queue(5, 2)
    job.meta["progress"] = 100
    job.save_meta()

    queued_task = Task(id=job.id, name="Add", description="Add task")
    session.add(queued_task)
    session.commit()

    assert queued_task.get_progress() == 100


def test_run_async_task_get_job_from_task(app, rq, session):
    rq.job(add)
    job = add.queue(5, 2)

    queued_task = Task(id=job.id, name="Add", description="Add task")
    session.add(queued_task)
    session.commit()

    retrieved_job = queued_task.get_rq_job()

    assert retrieved_job.id == job.id
