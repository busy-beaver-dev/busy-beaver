import pytest

from busy_beaver.blueprints.slack.slash_command import (
    command_not_found,
    disconnect_github,
    display_help_text,
    link_github,
    next_event,
    relink_github,
    upcoming_events,
)
from busy_beaver.config import FULL_INSTALLATION_WORKSPACE_IDS
from busy_beaver.factories.event import EventFactory
from busy_beaver.models import User


@pytest.fixture
def add_user(session):
    def _add_user(username):
        user = User(slack_id=username)
        session.add(user)
        session.commit()
        return user

    return _add_user


@pytest.fixture
def generate_slash_command_request():
    def _generate_data(
        command,
        user_id="U5FRZAD323",
        channel_id="CFLDRNBSDFD",
        team_id="T5GCMNWAFSDFSDF",
    ):
        return {
            "token": "deprecated",
            "team_id": team_id,
            "team_domain": "cant-depend-on-this",
            "channel_id": channel_id,
            "channel_name": "cant-depend-on-this",
            "user_id": user_id,
            "user_name": "cant-depend-on-this",
            "command": "/busybeaver",
            "text": command,
            "response_url": "https://hooks.slack.com/commands/T5GCMNW/639192748/39",
            "trigger_id": "639684516021.186015429778.0a18640db7b29f98749b62f6e824fe30",
        }

    return _generate_data


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


#########################
# Upcoming Event Schedule
#########################
@pytest.mark.end2end
def test_command_next_workspace_not_allowed(session, generate_slash_command_request):
    events = EventFactory.create_batch(size=10)
    [session.add(event) for event in events]
    session.commit()
    data = generate_slash_command_request("next", team_id="not allowed")

    result = next_event(**data)

    assert "command not supported" in result.json["text"].lower()


@pytest.mark.end2end
def test_command_next_workspace_allowed(session, generate_slash_command_request):
    events = EventFactory.create_batch(size=10)
    [session.add(event) for event in events]
    session.commit()
    workspace_id = FULL_INSTALLATION_WORKSPACE_IDS[0]
    data = generate_slash_command_request("next", team_id=workspace_id)

    result = next_event(**data)

    assert result.json["response_type"] == "ephemeral"
    assert result.json["attachments"]
    assert not result.json["blocks"]
    assert not result.json["text"]


@pytest.mark.end2end
def test_command_events_workspace_not_allowed(session, generate_slash_command_request):
    events = EventFactory.create_batch(size=10)
    [session.add(event) for event in events]
    session.commit()
    data = generate_slash_command_request("events", team_id="not_allowed")

    result = upcoming_events(**data)

    assert "command not supported" in result.json["text"].lower()


@pytest.mark.end2end
def test_command_events_workspace_allowed(session, generate_slash_command_request):
    events = EventFactory.create_batch(size=10)
    [session.add(event) for event in events]
    session.commit()
    workspace_id = FULL_INSTALLATION_WORKSPACE_IDS[0]
    data = generate_slash_command_request("events", team_id=workspace_id)

    result = upcoming_events(**data)

    assert result.json["response_type"] == "ephemeral"
    assert result.json["blocks"]
    assert not result.json["attachments"]
    assert not result.json["text"]


########################
# Miscellaneous Commands
########################
@pytest.mark.unit
def test_command_help(generate_slash_command_request):
    data = generate_slash_command_request("help")

    result = display_help_text(**data)

    assert "/busybeaver help" in result.json["text"]


@pytest.mark.unit
def test_command_not_found(generate_slash_command_request):
    data = generate_slash_command_request(command="blah")

    result = command_not_found(**data)

    assert "/busybeaver help" in result.json["text"]


##########################################
# Associate GitHub account with Slack user
##########################################
@pytest.mark.unit
def test_connect_command_new_user(session, generate_slash_command_request):
    data = generate_slash_command_request("connect", user_id="new_user")

    result = link_github(**data)

    slack_response = result.json["attachments"][0]
    assert "Associate GitHub Profile" in slack_response["actions"][0]["text"]


@pytest.mark.unit
def test_connect_command_existing_user(add_user, generate_slash_command_request):
    add_user(username="existing_user")
    data = generate_slash_command_request("connect", user_id="existing_user")

    result = link_github(**data)

    assert "/busybeaver reconnect" in result.json["text"]


@pytest.mark.unit
def test_reconnect_command_new_user(session, generate_slash_command_request):
    data = generate_slash_command_request("reconnect", user_id="new_user")

    result = relink_github(**data)

    assert "/busybeaver connect" in result.json["text"]


@pytest.mark.unit
def test_reconnect_command_existing_user(generate_slash_command_request, add_user):
    add_user(username="existing_user")
    data = generate_slash_command_request("reconnect", user_id="existing_user")

    result = relink_github(**data)

    slack_response = result.json["attachments"][0]
    assert "Associate GitHub Profile" in slack_response["actions"][0]["text"]


@pytest.mark.unit
def test_disconnect_command_unregistered_user(session, generate_slash_command_request):
    data = generate_slash_command_request("disconnect")

    result = disconnect_github(**data)

    assert "No GitHub account associated with profile" in result.json["text"]


@pytest.mark.unit
def test_disconnect_command_registered_user(
    session, generate_slash_command_request, add_user
):
    user = add_user("existing_user")
    data = generate_slash_command_request("disconnect", user_id="existing_user")

    result = disconnect_github(**data)

    assert "Account has been deleted" in result.json["text"]
    assert not User.query.get(user.id)
