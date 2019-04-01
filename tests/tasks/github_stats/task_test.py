from typing import List
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
    assert task.job_id == patched_background_task.id
    assert task.data["channel_name"] == channel_name
    assert "boundary_dt" in task.data


#####################
# Test Background Job
#####################
@pytest.fixture
def patched_slack(mocker, patcher):
    class FakeSlackClient:
        def __init__(self, *, channel_info):
            self.mock = mocker.MagicMock()
            if channel_info:
                self.channel_info = channel_info

        def get_channel_info(self, *args, **kwargs):
            self.mock(*args, **kwargs)
            return self.channel_info

        def post_message(self, *args, **kwargs):
            self.mock(*args, **kwargs)
            return

        def __repr__(self):
            return "<FakeSlackClient>"

    def _wrapper(*, channel_info=None):
        obj = FakeSlackClient(channel_info=channel_info)
        return patcher(MODULE_TO_TEST, namespace="slack", replacement=obj)

    return _wrapper


@pytest.fixture
def patched_github_user_events(mocker, patcher):
    class FakeGitHubUserEvents:
        def __init__(self, *, summary_messages: List[str]):
            self.mock = mocker.MagicMock(side_effect=list(summary_messages))

        def generate_summary_text(self, *args, **kwargs):
            return self.mock(*args, **kwargs)

        def __call__(self, *args, **kwargs):
            return self

        def __repr__(self):
            return "<FakeGitHubUserEvents>"

    def _wrapper(*, messages=None):
        obj = FakeGitHubUserEvents(summary_messages=messages)
        return patcher(MODULE_TO_TEST, namespace="GitHubUserEvents", replacement=obj)

    return _wrapper


@pytest.mark.unit
def test_fetch_github_summary_post_to_slack_with_no_users(
    session, t_minus_one_day, patched_slack, patched_github_user_events
):
    # Arrange
    boundary_dt = t_minus_one_day
    channel_info = Channel(name="general", id="idz", members=["user1", "user2"])
    slack = patched_slack(channel_info=channel_info)
    patched_github_user_events(messages=["a", "b"])

    # Act
    fetch_github_summary_post_to_slack("general", boundary_dt=boundary_dt)

    # Assert
    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "does it make a sound" in kwargs["message"]
    assert "idz" in kwargs["channel_id"]


@pytest.mark.unit
def test_fetch_github_summary_post_to_slack_with_no_activity(
    session, create_user, t_minus_one_day, patched_slack, patched_github_user_events
):
    # Arrange
    boundary_dt = t_minus_one_day
    create_user(slack_id="user1", github_username="user1")
    channel_info = Channel(name="general", id="idz", members=["user1", "user2"])
    slack = patched_slack(channel_info=channel_info)
    patched_github_user_events(messages=[""])

    # Act
    fetch_github_summary_post_to_slack("general", boundary_dt=boundary_dt)

    # Assert
    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "does it make a sound" in kwargs["message"]


@pytest.mark.unit
def test_fetch_github_summary_post_to_slack_with_activity(
    session, create_user, t_minus_one_day, patched_slack, patched_github_user_events
):
    # Arrange
    boundary_dt = t_minus_one_day
    create_user(slack_id="user1", github_username="user1")
    create_user(slack_id="user2", github_username="user2")
    channel_info = Channel(name="general", id="idz", members=["user1", "user2"])
    slack = patched_slack(channel_info=channel_info)
    patched_github_user_events(messages=["a", "b"])

    # Act
    fetch_github_summary_post_to_slack("general", boundary_dt=boundary_dt)

    # Assert
    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "ab" in kwargs["message"]


@pytest.mark.vcr()
@pytest.mark.freeze_time("2019-03-31")
@pytest.mark.integration
def test_post_github_summary_task__integration(
    session, create_user, t_minus_one_day, patched_slack
):
    channel_info = Channel(name="general", id="idz", members=["user1", "user2"])
    slack = patched_slack(channel_info=channel_info)
    create_user(slack_id="user1", github_username="alysivji")

    # Act
    fetch_github_summary_post_to_slack("general", boundary_dt=t_minus_one_day)

    # Assert
    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "<@user1>" in kwargs["message"]
