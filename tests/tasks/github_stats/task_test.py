import pytest

from busy_beaver.adapters.slack import Channel
from busy_beaver.models import ApiUser
from busy_beaver.tasks.github_stats.task import (
    start_post_github_summary_task,
    fetch_github_summary_post_to_slack,
)

MODULE_TO_TEST = "busy_beaver.tasks.github_stats.task"


#######################
# Test Trigger Function
#######################
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


######################
# Test Background Task
######################
@pytest.fixture
def patched_slack_get_channel_info(patcher):
    def _wrapper(channel_name, *, channel_id, members):
        return patcher(
            MODULE_TO_TEST,
            namespace="slack.get_channel_info",
            replacement=Channel(name=channel_name, id=channel_id, members=members),
        )

    return _wrapper


def test_fetch_github_summary_post_to_slack__with_no_users(
    patched_slack_get_channel_info
):
    patched_slack_get_channel_info("test", channel_id="test_id", members=["abc", "def"])

    # call function
    message = fetch_github_summary_post_to_slack("test", None)

    # Assert
    assert "does it make a sound?" in message


def test_fetch_github_summary_post_to_slack__with_users():
    # patch slack.get_channel_info()
    # add two users to the database
    pass
