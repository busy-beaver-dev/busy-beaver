from datetime import time

import pytest

from busy_beaver.apps.github_integration.cli import (
    _get_time_to_post,
    queue_github_summary_jobs_for_tomorrow,
)
from busy_beaver.apps.github_integration.summary.workflow import (
    post_github_summary_message,
)
from busy_beaver.models import Task


@pytest.mark.freeze_time("2020-07-08")
def test_correct_time_to_post(factory):
    config = factory.GitHubSummaryConfiguration(
        summary_post_time=time(14, 00), summary_post_timezone="America/Chicago"
    )

    result = _get_time_to_post(config)

    assert result.time() == time(19, 00)


#######################
# Test Trigger Function
#######################
@pytest.fixture
def patched_background_task(patcher, create_fake_background_task):
    return patcher(
        "busy_beaver.apps.github_integration.cli",
        namespace=post_github_summary_message.__name__,
        replacement=create_fake_background_task(),
    )


@pytest.mark.unit
def test_queue_github_summary_jobs_for_tomorrow_task(
    runner, session, factory, patched_background_task
):
    """Test trigger function"""
    # Arrange
    slack_installation = factory.SlackInstallation(workspace_id="abc")
    factory.GitHubSummaryConfiguration(
        enabled=True,
        summary_post_time=time(14, 00),
        summary_post_timezone="America/Chicago",
        slack_installation=slack_installation,
    )

    slack_installation = factory.SlackInstallation(workspace_id="second_workspace")
    factory.GitHubSummaryConfiguration(
        enabled=False,
        summary_post_time=time(14, 00),
        summary_post_timezone="America/Chicago",
        slack_installation=slack_installation,
    )

    # Act
    runner.invoke(queue_github_summary_jobs_for_tomorrow)

    # Assert
    tasks = Task.query.all()
    assert len(tasks) == 1

    task = tasks[0]
    assert task is not None
    assert task.job_id == patched_background_task.id
    assert task.data["workspace_id"] == "abc"


@pytest.mark.unit
def test_queue_github_summary_jobs_for_tomorrow_task__does_not_have_time_set(
    runner, session, factory, patched_background_task, caplog
):
    """Test trigger function"""
    # Arrange
    slack_installation = factory.SlackInstallation(workspace_id="abc")
    factory.GitHubSummaryConfiguration(
        enabled=True,
        summary_post_time=None,
        summary_post_timezone="America/Chicago",
        slack_installation=slack_installation,
    )

    # Act
    runner.invoke(queue_github_summary_jobs_for_tomorrow)

    # Assert
    tasks = Task.query.all()
    assert len(tasks) == 0

    assert "ERROR" in caplog.text
    assert "No time to post configuration" in caplog.text
