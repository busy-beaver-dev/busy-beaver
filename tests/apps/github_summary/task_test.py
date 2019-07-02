from datetime import timedelta
from typing import List
import pytest

from busy_beaver.adapters.slack import Channel
from busy_beaver.models import ApiUser
from busy_beaver.apps.github_summary.task import (
    start_post_github_summary_task,
    fetch_github_summary_post_to_slack,
)
from busy_beaver.toolbox import utc_now_minus
from tests._utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.apps.github_summary.task"


@pytest.fixture
def t_minus_one_day():
    return utc_now_minus(timedelta(days=1))


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
def test_start_post_github_summary_task(session, factory, patched_background_task):
    """Test trigger function"""
    # Arrange
    slack_installation = factory.SlackInstallation(workspace_id="abc")
    api_user = factory.ApiUser(username="admin")

    # Act
    start_post_github_summary_task(api_user, slack_installation.workspace_id)

    # Assert
    api_user = ApiUser.query.get(api_user.id)
    task = api_user.tasks[0]
    assert task.job_id == patched_background_task.id
    assert task.data["slack_installation_id"] == slack_installation.id
    assert "boundary_dt" in task.data


#####################
# Test Background Job
#####################
@pytest.fixture
def patched_slack(patcher):
    def _wrapper(channel_info):
        obj = FakeSlackClient(channel_info=channel_info)
        return patcher(MODULE_TO_TEST, namespace="SlackAdapter", replacement=obj)

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
    session, factory, t_minus_one_day, patched_slack, patched_github_user_events
):
    # Arrange
    channel = "general"
    boundary_dt = t_minus_one_day
    github_summary_config = factory.GitHubSummaryConfiguration(channel=channel)
    slack_installation = github_summary_config.slack_installation
    channel_info = Channel(name="general", members=["user1", "user2"])
    slack = patched_slack(channel_info=channel_info)
    patched_github_user_events(messages=["a", "b"])

    # Act
    fetch_github_summary_post_to_slack(
        installation_id=slack_installation.id, boundary_dt=boundary_dt
    )

    # Assert
    slack_adapter_initalize_args = slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert slack_installation.bot_access_token in args

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "does it make a sound" in kwargs["message"]
    assert "general" in kwargs["channel"]


@pytest.mark.unit
def test_fetch_github_summary_post_to_slack_with_no_activity(
    session, factory, t_minus_one_day, patched_slack, patched_github_user_events
):
    # Arrange
    channel = "general"
    boundary_dt = t_minus_one_day
    github_summary_config = factory.GitHubSummaryConfiguration(channel=channel)
    slack_installation = github_summary_config.slack_installation
    factory.GitHubSummaryUser(
        slack_id="user1",
        github_username="github_user1",
        installation=slack_installation,
    )
    channel_info = Channel(name="general", members=["user1", "user2"])
    slack = patched_slack(channel_info=channel_info)
    patched_github_user_events(messages=[""])

    # Act
    fetch_github_summary_post_to_slack(
        installation_id=slack_installation.id, boundary_dt=boundary_dt
    )

    # Assert
    slack_adapter_initalize_args = slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert slack_installation.bot_access_token in args

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "does it make a sound" in kwargs["message"]


@pytest.mark.unit
def test_fetch_github_summary_post_to_slack_with_activity(
    session, factory, t_minus_one_day, patched_slack, patched_github_user_events
):
    # Arrange
    channel = "general"
    boundary_dt = t_minus_one_day
    github_summary_config = factory.GitHubSummaryConfiguration(channel=channel)
    slack_installation = github_summary_config.slack_installation
    factory.GitHubSummaryUser(
        slack_id="user1",
        github_username="github_user1",
        installation=slack_installation,
    )
    factory.GitHubSummaryUser(
        slack_id="user2",
        github_username="github_user2",
        installation=slack_installation,
    )
    channel_info = Channel(name="general", members=["user1", "user2"])
    slack = patched_slack(channel_info=channel_info)
    patched_github_user_events(messages=["a", "b"])

    # Act
    fetch_github_summary_post_to_slack(
        installation_id=slack_installation.id, boundary_dt=boundary_dt
    )

    # Assert
    slack_adapter_initalize_args = slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert slack_installation.bot_access_token in args

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "ab" in kwargs["message"]


@pytest.mark.vcr()
@pytest.mark.freeze_time("2019-03-31")
@pytest.mark.integration
def test_post_github_summary_task__integration(
    session, factory, t_minus_one_day, patched_slack
):
    channel = "general"
    github_summary_config = factory.GitHubSummaryConfiguration(channel=channel)
    slack_installation = github_summary_config.slack_installation
    factory.GitHubSummaryUser(
        slack_id="user1", github_username="alysivji", installation=slack_installation
    )

    channel_info = Channel(name="general", members=["user1", "user2"])
    slack = patched_slack(channel_info=channel_info)

    # Act
    fetch_github_summary_post_to_slack(
        installation_id=slack_installation.id, boundary_dt=t_minus_one_day
    )

    # Assert
    slack_adapter_initalize_args = slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert slack_installation.bot_access_token in args

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "<@user1>" in kwargs["message"]
