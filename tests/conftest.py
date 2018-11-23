import pytest

from adapters.github_adapter_sync import GitHubAdapterSync


@pytest.fixture
def client():
    yield GitHubAdapterSync(oauth_token="test_token")

