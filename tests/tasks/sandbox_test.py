from busy_beaver.tasks.sandbox import add


def test_add(app):
    assert add(5, 2) == 7


def test_add_task_queue(app):
    job = add.queue(5, 2)
    assert job.result == 7
