import pytest

from busy_beaver.apps.slack_integration.models import SlackUser

pytest_plugins = ("tests._utilities.fixtures.slack",)


###################
# Integration Tests
###################
@pytest.mark.integration
def test_slack_command_valid_command(
    client, session, factory, create_slack_headers, generate_slash_command_request
):
    installation = factory.SlackInstallation()
    data = generate_slash_command_request("help", team_id=installation.workspace_id)
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack/slash-command", headers=headers, data=data)

    assert response.status_code == 200
    assert "/busybeaver help" in response.json["text"].lower()


@pytest.mark.integration
def test_slack_command_invalid_command(
    client, session, factory, create_slack_headers, generate_slash_command_request
):
    installation = factory.SlackInstallation()
    data = generate_slash_command_request(
        "non-existent", team_id=installation.workspace_id
    )
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack/slash-command", headers=headers, data=data)

    assert response.status_code == 200
    assert "command not found" in response.json["text"].lower()


@pytest.mark.integration
def test_slack_command_empty_command(
    client, session, factory, create_slack_headers, generate_slash_command_request
):
    installation = factory.SlackInstallation()
    data = generate_slash_command_request(command="", team_id=installation.workspace_id)
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack/slash-command", headers=headers, data=data)

    assert response.status_code == 200
    assert "/busybeaver help" in response.json["text"].lower()


@pytest.mark.integration
def test_slack_command_creates_user_record_in_database(
    client, session, factory, create_slack_headers, generate_slash_command_request
):
    # Arrange
    installation = factory.SlackInstallation()
    data = generate_slash_command_request("help", team_id=installation.workspace_id)
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    # Act
    client.post("/slack/slash-command", headers=headers, data=data)

    # Assert
    users = SlackUser.query.all()
    assert len(users) == 1

    user = users[0]
    assert user.slack_id == data["user_id"]
    assert user.installation.workspace_id == data["team_id"]
