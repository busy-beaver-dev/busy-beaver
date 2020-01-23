import pytest

from busy_beaver.apps.slack_integration.slash_command import (
    command_not_found,
    disconnect_github,
    display_help_text,
    link_github,
    next_event,
    relink_github,
    upcoming_events,
)
from busy_beaver.config import FULL_INSTALLATION_WORKSPACE_IDS
from busy_beaver.models import GitHubSummaryUser

pytest_plugins = ("tests._utilities.fixtures.slack",)


@pytest.fixture
def add_user(session):
    def _add_user(username, installation):
        user = GitHubSummaryUser(slack_id=username)
        user.installation = installation
        session.add(user)
        session.commit()
        return user

    return _add_user


########################
# Miscellaneous Commands
########################
@pytest.mark.unit
def test_command_help(generate_slash_command_request):
    data = generate_slash_command_request("help")

    result = display_help_text(**data)

    assert "/busybeaver help" in result["text"]


@pytest.mark.unit
def test_command_not_found(generate_slash_command_request):
    data = generate_slash_command_request(command="blah")

    result = command_not_found(**data)

    assert "/busybeaver help" in result["text"]


##########################################
# Associate GitHub account with Slack user
##########################################
@pytest.mark.unit
def test_connect_command_new_user(session, factory, generate_slash_command_request):
    workspace_id = "test_id"
    factory.SlackInstallation(workspace_id=workspace_id)
    data = generate_slash_command_request(
        "connect", user_id="new_user", team_id=workspace_id
    )

    result = link_github(**data)

    slack_response = result["attachments"][0]
    assert "Associate GitHub Profile" in slack_response["actions"][0]["text"]


@pytest.mark.unit
def test_connect_command_existing_user(
    session, factory, add_user, generate_slash_command_request
):
    workspace_id = "test_id"
    slack_installation = factory.SlackInstallation(workspace_id=workspace_id)
    add_user(username="existing_user", installation=slack_installation)
    data = generate_slash_command_request(
        "connect", user_id="existing_user", team_id=workspace_id
    )

    result = link_github(**data)

    assert "/busybeaver reconnect" in result["text"]


@pytest.mark.unit
def test_reconnect_command_new_user(session, factory, generate_slash_command_request):
    workspace_id = "test_id"
    factory.SlackInstallation(workspace_id=workspace_id)
    data = generate_slash_command_request(
        "reconnect", user_id="new_user", team_id=workspace_id
    )

    result = relink_github(**data)

    assert "/busybeaver connect" in result["text"]


@pytest.mark.unit
def test_reconnect_command_existing_user(
    session, factory, generate_slash_command_request, add_user
):
    workspace_id = "test_id"
    slack_installation = factory.SlackInstallation(workspace_id=workspace_id)
    add_user(username="existing_user", installation=slack_installation)
    data = generate_slash_command_request(
        "reconnect", user_id="existing_user", team_id=workspace_id
    )

    result = relink_github(**data)

    slack_response = result["attachments"][0]
    assert "Associate GitHub Profile" in slack_response["actions"][0]["text"]


@pytest.mark.unit
def test_disconnect_command_unregistered_user(
    session, factory, generate_slash_command_request
):
    workspace_id = "test_id"
    factory.SlackInstallation(workspace_id=workspace_id)
    data = generate_slash_command_request("disconnect", team_id=workspace_id)

    result = disconnect_github(**data)

    assert "No GitHub account associated with profile" in result["text"]


@pytest.mark.unit
def test_disconnect_command_registered_user(
    session, factory, generate_slash_command_request, add_user
):
    workspace_id = "test_id"
    slack_installation = factory.SlackInstallation(workspace_id=workspace_id)
    user = add_user(username="existing_user", installation=slack_installation)
    data = generate_slash_command_request(
        "disconnect", user_id="existing_user", team_id=workspace_id
    )

    result = disconnect_github(**data)

    assert "Account has been deleted" in result["text"]
    assert not GitHubSummaryUser.query.get(user.id)


#########################
# Upcoming Event Schedule
#########################
@pytest.mark.end2end
def test_command_next_workspace_not_allowed(
    session, factory, generate_slash_command_request
):
    factory.Event.create_batch(size=10)
    data = generate_slash_command_request("next", team_id="not allowed")

    result = next_event(**data)

    assert "command not supported" in result["text"].lower()


@pytest.mark.end2end
def test_command_next_workspace_allowed(
    session, factory, generate_slash_command_request
):
    factory.Event.create_batch(size=10)
    workspace_id = FULL_INSTALLATION_WORKSPACE_IDS[0]
    data = generate_slash_command_request("next", team_id=workspace_id)

    result = next_event(**data)

    assert result["response_type"] == "ephemeral"
    assert result["attachments"]
    assert not result["blocks"]
    assert not result["text"]


@pytest.mark.end2end
def test_command_events_workspace_not_allowed(
    session, factory, generate_slash_command_request
):
    factory.Event.create_batch(size=10)
    data = generate_slash_command_request("events", team_id="not_allowed")

    result = upcoming_events(**data)

    assert "command not supported" in result["text"].lower()


@pytest.mark.end2end
def test_command_events_workspace_allowed(
    session, factory, generate_slash_command_request
):
    factory.Event.create_batch(size=10)
    workspace_id = FULL_INSTALLATION_WORKSPACE_IDS[0]
    data = generate_slash_command_request("events", team_id=workspace_id)

    result = upcoming_events(**data)

    assert result["response_type"] == "ephemeral"
    assert result["blocks"]
    assert not result["attachments"]
    assert not result["text"]
