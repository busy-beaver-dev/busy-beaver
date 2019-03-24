from busy_beaver.models import Task


def test_create_task(session):
    task = Task(
        id="abcd",
        name="task_created_for_test",
        description="Task created for testing purposes",
    )

    session.add(task)
    session.commit()

    assert task.complete is False
    assert task.failed is False
