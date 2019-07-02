import pytest


@pytest.fixture(scope="session")
def vcr_config():
    """Overwrite headers and query parameters where key can be leaked"""
    return {
        "filter_headers": [("authorization", "DUMMY")],
        "filter_query_parameters": ["key"],
    }
