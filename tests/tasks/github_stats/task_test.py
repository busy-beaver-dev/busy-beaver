import pytest

from busy_beaver.models import ApiUser
from busy_beaver.tasks.github_stats.task import (
    start_post_github_summary_task,
    fetch_github_summary_post_to_slack,
)


MODULE_TO_TEST = "busy_beaver.tasks.github_stats.task"


@pytest.fixture
def patched_background_task(patcher, create_fake_background_task):
    return patcher(
        MODULE_TO_TEST,
        namespace=fetch_github_summary_post_to_slack.__name__,
        replacement=create_fake_background_task(),
    )


@pytest.mark.unit
def test_start_post_github_summary_task(
    session, patched_background_task, create_api_user
):
    """Test trigger function"""
    # Arrange
    api_user = create_api_user("admin")
    channel_name = "test-channel"

    # Act
    start_post_github_summary_task(api_user, channel_name)

    # Assert
    api_user = ApiUser.query.get(api_user.id)
    task = api_user.tasks[0]
    assert task.id == patched_background_task.id
    assert task.data["channel_name"] == channel_name
    assert "boundary_dt" in task.data
