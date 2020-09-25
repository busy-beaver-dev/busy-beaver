import pytest

from busy_beaver.apps.call_for_proposals.cli import post_upcoming_cfps
from tests._utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.apps.call_for_proposals.cli"


@pytest.fixture
def patched_slack(patcher):
    obj = FakeSlackClient()
    return patcher(MODULE_TO_TEST, namespace="SlackClient", replacement=obj)


@pytest.mark.end2end
@pytest.mark.vcr
def test_post_upcoming_cfps(mocker, runner, factory, patched_slack):
    # Arrange
    config = factory.CallForProposalsConfiguration(enabled=True)

    # Act
    runner.invoke(post_upcoming_cfps)

    # Assert
    assert patched_slack.mock.call_count == 2

    slack_adapter_initalize_args = patched_slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert config.slack_installation.bot_access_token in args

    post_message_args = patched_slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "blocks" in kwargs
    assert len(kwargs["blocks"]) == 5


@pytest.mark.end2end
@pytest.mark.vcr
def test_post_upcoming_cfps_enabled(mocker, runner, factory, patched_slack):
    """Only post for configurations that are enabled

    Should have 2 calls:
        - when initialized
        - when post_message is called
    """
    # Arrange
    factory.CallForProposalsConfiguration(enabled=False)
    factory.CallForProposalsConfiguration(enabled=True)

    # Act
    runner.invoke(post_upcoming_cfps)

    # Assert
    assert patched_slack.mock.call_count == 2
