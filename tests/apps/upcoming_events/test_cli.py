import calendar
from datetime import date, time, timedelta

import pytest

from busy_beaver.apps.upcoming_events.cli import (
    _get_time_to_post,
    queue_upcoming_events_jobs_for_tomorrow,
)
from busy_beaver.apps.upcoming_events.workflow import post_upcoming_events_message
from busy_beaver.models import Task


@pytest.mark.freeze_time("2020-07-08")
def test_correct_time_to_post(factory):
    config = factory.UpcomingEventsConfiguration(
        post_time=time(14, 00), post_timezone="America/Chicago"
    )

    result = _get_time_to_post(config)

    assert result.time() == time(19, 00)


#######################
# Test Trigger Function
#######################
@pytest.fixture
def patched_background_task(patcher, create_fake_background_task):
    return patcher(
        "busy_beaver.apps.upcoming_events.cli",
        namespace=post_upcoming_events_message.__name__,
        replacement=create_fake_background_task(),
    )


@pytest.mark.unit
def test_queue_upcoming_events_jobs_for_tomorrow_task(
    runner, session, factory, patched_background_task
):
    """Test trigger function"""
    # Arrange
    tomorrow = date.today() + timedelta(days=1)
    tomorrow_day_of_week = calendar.day_name[tomorrow.weekday()]
    slack_installation = factory.SlackInstallation(workspace_id="abc")
    factory.UpcomingEventsConfiguration(
        enabled=True,
        post_day_of_week=tomorrow_day_of_week,
        post_time=time(14, 00),
        post_timezone="America/Chicago",
        slack_installation=slack_installation,
    )

    yesterday = date.today() - timedelta(days=1)
    yesterday_day_of_week = calendar.day_name[yesterday.weekday()]
    slack_installation = factory.SlackInstallation(workspace_id="second_workspace")
    factory.UpcomingEventsConfiguration(
        enabled=True,
        post_day_of_week=yesterday_day_of_week,
        post_time=time(14, 00),
        post_timezone="America/Chicago",
        slack_installation=slack_installation,
    )

    # Act
    runner.invoke(queue_upcoming_events_jobs_for_tomorrow)

    # Assert
    tasks = Task.query.all()
    assert len(tasks) == 1

    task = tasks[0]
    assert task is not None
    assert task.name == "post_upcoming_events_message"
    assert task.job_id == patched_background_task.id
    assert task.data["config_id"] == 1
