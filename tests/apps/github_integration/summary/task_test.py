from datetime import timedelta
import json
from typing import List

import pytest

from busy_beaver.apps.github_integration.cli import post_github_summary_to_slack_cli
from busy_beaver.apps.github_integration.summary.task import (
    fetch_github_summary_post_to_slack,
)
from busy_beaver.toolbox import utc_now_minus
from tests._utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.apps.github_integration.summary.task"


@pytest.fixture
def t_minus_one_day():
    return utc_now_minus(timedelta(days=1))


@pytest.fixture
def patched_slack(patcher):
    def _wrapper(members):
        obj = FakeSlackClient(members=members)
        return patcher(MODULE_TO_TEST, namespace="SlackClient", replacement=obj)

    return _wrapper


@pytest.fixture
def patched_github_user_events(mocker, patcher):
    class FakeGitHubUserEvents:
        def __init__(self, *, summary_messages: List[str]):
            self.summary_messages = summary_messages
            self.mock = mocker.MagicMock(side_effect=list(summary_messages))

        def generate_summary_text(self, *args, **kwargs):
            return self.mock(*args, **kwargs)

        def __call__(self, *args, **kwargs):
            return self

        def __repr__(self):
            return "<FakeGitHubUserEvents>"

        def __len__(self):
            return len(self.summary_messages)

    def _wrapper(*, messages=None):
        obj = FakeGitHubUserEvents(summary_messages=messages)
        return patcher(
            "busy_beaver.apps.github_integration.summary.blocks",
            namespace="GitHubUserEvents",
            replacement=obj,
        )

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
    slack = patched_slack(members=["user1", "user2"])
    patched_github_user_events(messages=["a", "b"])

    # Act
    fetch_github_summary_post_to_slack(
        installation=slack_installation, boundary_dt=boundary_dt
    )

    # Assert
    slack_adapter_initalize_args = slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert slack_installation.bot_access_token in args

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "No activity to report" in json.dumps(kwargs["blocks"])
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
        configuration=slack_installation.github_summary_config,
    )
    slack = patched_slack(members=["user1", "user2"])
    patched_github_user_events(messages=[])

    # Act
    fetch_github_summary_post_to_slack(
        installation=slack_installation, boundary_dt=boundary_dt
    )

    # Assert
    slack_adapter_initalize_args = slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert slack_installation.bot_access_token in args

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "No activity to report" in json.dumps(kwargs["blocks"])


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
        configuration=slack_installation.github_summary_config,
    )
    factory.GitHubSummaryUser(
        slack_id="user2",
        github_username="github_user2",
        configuration=slack_installation.github_summary_config,
    )
    slack = patched_slack(members=["user1", "user2"])
    patched_github_user_events(messages=["a", "b"])

    # Act
    fetch_github_summary_post_to_slack(
        installation=slack_installation, boundary_dt=boundary_dt
    )

    # Assert
    slack_adapter_initalize_args = slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert slack_installation.bot_access_token in args

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert len(kwargs["blocks"]) == 6


@pytest.mark.vcr()
@pytest.mark.freeze_time("2019-03-31")
@pytest.mark.integration
def test_fetch_github_summary_post_to_slack(
    session, factory, t_minus_one_day, patched_slack
):
    channel = "general"
    github_summary_config = factory.GitHubSummaryConfiguration(channel=channel)
    slack_installation = github_summary_config.slack_installation
    factory.GitHubSummaryUser(
        slack_id="user1",
        github_username="alysivji",
        configuration=slack_installation.github_summary_config,
    )
    slack = patched_slack(members=["user1", "user2"])

    # Act
    fetch_github_summary_post_to_slack(
        installation=slack_installation, boundary_dt=t_minus_one_day
    )

    # Assert
    slack_adapter_initalize_args = slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert slack_installation.bot_access_token in args

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "<@user1>" in json.dumps(kwargs["blocks"])


##########
# Test CLI
##########
@pytest.mark.end2end
def test_post_github_summary_to_slack_cli(
    runner, session, factory, t_minus_one_day, patched_slack, patched_github_user_events
):
    # Arrange
    slack_installation = factory.SlackInstallation(workspace_id="abc")
    channel = "general"
    github_summary_config = factory.GitHubSummaryConfiguration(
        channel=channel, slack_installation=slack_installation
    )
    slack_installation = github_summary_config.slack_installation
    slack = patched_slack(members=["user1", "user2"])
    patched_github_user_events(messages=["a", "b"])

    # Act
    runner.invoke(post_github_summary_to_slack_cli, ["--workspace", "abc"])

    # Assert
    slack_adapter_initalize_args = slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert slack_installation.bot_access_token in args

    post_message_args = slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "No activity to report" in json.dumps(kwargs["blocks"])
    assert "general" in kwargs["channel"]
