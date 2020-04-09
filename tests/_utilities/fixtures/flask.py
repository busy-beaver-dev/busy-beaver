import pytest

from busy_beaver.app import create_app


@pytest.fixture(scope="module")
def app():
    """Session-wide test `Flask` application.

    Establish an application context before running the tests.
    """
    app = create_app(testing=True)
    ctx = app.app_context()
    ctx.push()
    yield app

    ctx.pop()


@pytest.fixture(scope="module")
def client(app):
    """Create Flask test client where we can trigger test requests to app"""
    client = app.test_client()
    yield client


@pytest.fixture(scope="module")
def runner(app):
    """Create Flask CliRunner that can be used to invoke commands"""
    runner = app.test_cli_runner()
    yield runner
