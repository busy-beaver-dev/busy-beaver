import pytest
from redis.exceptions import RedisError
from rq.exceptions import NoSuchJobError

from busy_beaver.models import (
    NewEventsToDatabaseTask,
    PostGitHubSummaryTask,
    PostTweetTask,
    Task,
)

MODULE_TO_TEST = "busy_beaver.models.task"


###########
# Base Task
###########
def test_create_task(session):
    # Arrange
    task = Task(
        job_id="abcd",
        name="task_created_for_test",
        description="Task created for testing purposes",
    )

    # Act
    session.add(task)
    session.commit()

    # Assert
    assert task.job_id == "abcd"
    assert task.complete is False
    assert task.failed is False


def add(x, y):
    return x + y


def test_run_async_task_update_progress(app, rq, session):
    # Arrange
    rq.job(add)
    job = add.queue(5, 2)
    job.meta["progress"] = 100
    job.save_meta()

    # Act
    queued_task = Task(job_id=job.id, name="Add", description="Add task")
    session.add(queued_task)
    session.commit()

    # Assert
    assert queued_task.get_progress() == 100


def test_run_async_task_get_job_from_task(app, rq, session):
    # Arrange
    rq.job(add)
    job = add.queue(5, 2)

    queued_task = Task(job_id=job.id, name="Add", description="Add task")
    session.add(queued_task)
    session.commit()

    # Act
    retrieved_job = queued_task.get_rq_job()

    # Assert
    assert retrieved_job.id == job.id


@pytest.fixture
def patched_rq(patcher):
    def _wrapper(replacement):
        return patcher(MODULE_TO_TEST, namespace="Job", replacement=replacement)

    return _wrapper


@pytest.mark.parametrize("raise_exc", [RedisError, NoSuchJobError])
def test_task_model_get_job_raises_exception(app, rq, session, patched_rq, raise_exc):
    # Arrange
    class FakeJob:
        def __init__(self, error):
            self.error = error

        def fetch(self, *args, **kwargs):
            raise self.error

    patched_rq(FakeJob(raise_exc))

    rq.job(add)
    job = add.queue(5, 2)

    queued_task = Task(job_id=job.id, name="Add", description="Add task")
    session.add(queued_task)
    session.commit()

    # Act
    retrieved_job = queued_task.get_rq_job()

    # Assert
    assert retrieved_job is None


#####################
# GitHub Summary Task
#####################
def test_post_github_summary_task(session):
    # Arrange
    channel_name = "test-channel"
    task = PostGitHubSummaryTask(
        job_id="abcd",
        name="task_created_for_test",
        description="Task created for testing purposes",
        data={"channel_name": channel_name},
    )

    # Act
    session.add(task)
    session.commit()

    # Assert
    assert task.job_id == "abcd"
    assert task.complete is False
    assert task.failed is False
    assert task.data["channel_name"] == channel_name


#################
# Post Tweet Task
#################
def test_post_tweet_task(session):
    # Arrange
    channel_name = "test-channel"
    task = PostTweetTask(
        job_id="abcd",
        name="task_created_for_test",
        description="Task created for testing purposes",
        data={"channel_name": channel_name},
    )

    # Act
    session.add(task)
    session.commit()

    # Assert
    assert task.job_id == "abcd"
    assert task.complete is False
    assert task.failed is False
    assert task.data["channel_name"] == channel_name


#############################
# Update Events Database Task
#############################
def test_update_events_database_task(session):
    # Arrange
    task = NewEventsToDatabaseTask(
        job_id="abcd",
        name="task_created_for_test",
        description="Task created for testing purposes",
        data={"group_name": "_ChiPy_"},
    )

    # Act
    session.add(task)
    session.commit()

    # Assert
    assert task.job_id == "abcd"
    assert task.complete is False
    assert task.failed is False
    assert task.data["group_name"] == "_ChiPy_"
