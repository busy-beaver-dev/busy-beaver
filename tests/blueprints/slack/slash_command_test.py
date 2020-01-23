import pytest

pytest_plugins = ("tests._utilities.fixtures.slack",)


###################
# Integration Tests
###################
@pytest.mark.integration
def test_slack_command_valid_command(
    client, create_slack_headers, generate_slash_command_request
):
    data = generate_slash_command_request("help")
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack/slash-command", headers=headers, data=data)

    assert response.status_code == 200
    assert "/busybeaver help" in response.json["text"].lower()


@pytest.mark.integration
def test_slack_command_invalid_command(
    client, create_slack_headers, generate_slash_command_request
):
    data = generate_slash_command_request("non-existent")
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack/slash-command", headers=headers, data=data)

    assert response.status_code == 200
    assert "command not found" in response.json["text"].lower()


@pytest.mark.integration
def test_slack_command_empty_command(
    client, create_slack_headers, generate_slash_command_request
):
    data = generate_slash_command_request(command="")
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack/slash-command", headers=headers, data=data)

    assert response.status_code == 200
    assert "/busybeaver help" in response.json["text"].lower()
