import pytest

from busy_beaver.adapters.slack import SlackAdapter


MODULE_TO_TEST = "busy_beaver.adapters.slack"


@pytest.fixture
def fake_slack_client():
    class FakeSlackClient:
        def __init__(self, handler):
            self.function_handler = handler

        def api_call(self, *args, **kwargs):
            return self.function_handler

    def _wrapper(function_handler):
        return FakeSlackClient(function_handler)

    return _wrapper


@pytest.fixture
def patched_slack_client(patcher):
    def _wrapper(replacement):
        return patcher(MODULE_TO_TEST, namespace="SlackClient", replacement=replacement)

    return _wrapper


@pytest.mark.smoke
def test_create_slack_adapter(patched_slack_client, fake_slack_client):
    patched_slack_client(fake_slack_client())
    SlackAdapter("asdf")
    assert True
