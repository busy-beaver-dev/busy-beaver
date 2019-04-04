import pytest
from busy_beaver.blueprints.tasks.github_summary import start_post_github_summary_task

MODULE_TO_TEST = "busy_beaver.blueprints.tasks.github_summary"


@pytest.fixture
def patched_post_github_summary_trigger(mocker, patcher):
    return patcher(
        MODULE_TO_TEST,
        namespace=start_post_github_summary_task.__name__,
        replacement=mocker.Mock(),
    )


@pytest.mark.unit
def test_github_summary_endpoint_no_token(
    client, session, create_api_user, patched_post_github_summary_trigger
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="user")

    #  Act
    result = client.post("/github-summary")

    # Assert
    assert result.status_code == 401


@pytest.mark.unit
def test_github_summary_endpoint_incorrect_token(
    client, session, create_api_user, patched_post_github_summary_trigger
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="user")

    #  Act
    result = client.post("/github-summary")

    # Assert
    assert result.status_code == 401


@pytest.mark.unit
def test_github_summary_endpoint_empty_body(
    caplog, client, session, create_api_user, patched_post_github_summary_trigger
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="admin")

    #  Act
    result = client.post("/github-summary", headers={"Authorization": "token abcd"})

    # Assert
    assert result.status_code == 422


@pytest.mark.unit
def test_github_summary_endpoint_success(
    caplog, client, session, create_api_user, patched_post_github_summary_trigger
):
    # Arrange
    create_api_user(username="test_user", token="abcd", role="admin")
    mock = patched_post_github_summary_trigger

    #  Act
    result = client.post(
        "/github-summary",
        headers={"Authorization": "token abcd"},
        json={"channel": "general"},
    )

    # Assert
    assert result.status_code == 200
    args, kwargs = mock.call_args
    assert "general" in args
