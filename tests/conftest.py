import pytest


@pytest.fixture(scope="session")
def vcr_config():
    return {"filter_headers": [("authorization", "DUMMY")]}
