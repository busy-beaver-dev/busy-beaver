from datetime import timedelta
import json

import pytest

from busy_beaver.apps.github_integration.summary.workflow import (
    post_github_summary_message,
)
from busy_beaver.toolbox import utc_now_minus
from tests._utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.apps.github_integration.summary.workflow"


@pytest.fixture
def t_minus_one_day():
    return utc_now_minus(timedelta(days=1))


@pytest.fixture
def patched_slack(patcher):
    def _wrapper(members):
        obj = FakeSlackClient(members=members)
        return patcher(MODULE_TO_TEST, namespace="SlackClient", replacement=obj)

    return _wrapper


@pytest.mark.end2end
class TestPostGitHubSummaryMessage:
    @pytest.mark.vcr
    @pytest.mark.freeze_time("2021-08-28")
    def test_active_users_have_summary_generated(
        self,
        session,
        factory,
        patched_slack,
    ):
        # Arrange -- create GitHub Summary configuration
        channel = "general"
        github_summary_config = factory.GitHubSummaryConfiguration(channel=channel)

        # Arrange -- create user registered for GitHub Summary feature
        slack_user1 = "user1"
        factory.GitHubSummaryUser(
            slack_id=slack_user1,
            github_username="alysivji",
            configuration=github_summary_config,
        )

        # Arrange -- set up fake slack to return active users
        slack_installation = github_summary_config.slack_installation
        slack = patched_slack(members=[slack_user1, "user2"])

        # Act -- run function
        post_github_summary_message(workspace_id=slack_installation.workspace_id)

        # Assert -- message sent to slack has activity to report
        slack_adapter_initalize_args = slack.mock.call_args_list[0]
        args, kwargs = slack_adapter_initalize_args
        assert slack_installation.bot_access_token in args

        post_message_args = slack.mock.call_args_list[-1]
        args, kwargs = post_message_args
        assert f"<@{slack_user1}>" in json.dumps(kwargs["blocks"])  # check Slack handle
        assert "alysivji" in json.dumps(kwargs["blocks"])  # check GitHub handle
        assert "general" in kwargs["channel"]

    @pytest.mark.vcr
    @pytest.mark.freeze_time("2021-08-28")
    def test_inactive_users_results_in_no_activity_to_report(
        self,
        session,
        factory,
        patched_slack,
    ):
        # Arrange -- create GitHub Summary configuration
        channel = "general"
        github_summary_config = factory.GitHubSummaryConfiguration(channel=channel)

        # Arrange -- create user registered for GitHub Summary feature
        slack_user1 = "user1"
        factory.GitHubSummaryUser(
            slack_id=slack_user1,
            github_username="alysivji",
            configuration=github_summary_config,
        )

        # Arrange -- set up fake slack to return active users
        slack_installation = github_summary_config.slack_installation
        slack = patched_slack(members=["user78", "user34"])

        # Act -- run function
        post_github_summary_message(workspace_id=slack_installation.workspace_id)

        # Assert -- message sent to slack has activity to report
        slack_adapter_initalize_args = slack.mock.call_args_list[0]
        args, kwargs = slack_adapter_initalize_args
        assert slack_installation.bot_access_token in args

        post_message_args = slack.mock.call_args_list[-1]
        args, kwargs = post_message_args
        assert "no activity to report" in json.dumps(kwargs["blocks"]).lower()
        assert "general" in kwargs["channel"]
