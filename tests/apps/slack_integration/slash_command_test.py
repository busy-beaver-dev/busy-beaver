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
from busy_beaver.models import GitHubSummaryUser

pytest_plugins = ("tests._utilities.fixtures.slack",)


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
    github_summary_config = factory.GitHubSummaryConfiguration()
    install = github_summary_config.slack_installation
    new_user = "new_user"
    slack_user = factory.SlackUser(slack_id=new_user, installation=install)
    data = generate_slash_command_request(
        "connect", user_id=new_user, team_id=install.workspace_id
    )
    data["user"] = slack_user
    data["installation"] = install

    result = link_github(**data)

    slack_response = result["attachments"][0]
    assert "Associate GitHub Profile" in slack_response["actions"][0]["text"]


@pytest.mark.unit
def test_connect_command_existing_user(
    session, factory, generate_slash_command_request
):
    existing_user = "existing_user"
    github_user = factory.GitHubSummaryUser(slack_id=existing_user)
    install = github_user.configuration.slack_installation
    slack_user = factory.SlackUser(slack_id=existing_user, installation=install)
    data = generate_slash_command_request(
        "connect", user_id=github_user.slack_id, team_id=install.workspace_id
    )
    data["user"] = slack_user
    data["installation"] = install

    result = link_github(**data)

    assert "/busybeaver reconnect" in result["text"]


@pytest.mark.unit
def test_reconnect_command_new_user(session, factory, generate_slash_command_request):
    github_summary_config = factory.GitHubSummaryConfiguration()
    install = github_summary_config.slack_installation
    new_user = "new_user"
    slack_user = factory.SlackUser(slack_id=new_user, installation=install)
    data = generate_slash_command_request(
        "reconnect", user_id=new_user, team_id=install.workspace_id
    )
    data["user"] = slack_user
    data["installation"] = install

    result = relink_github(**data)

    slack_response = result["attachments"][0]
    assert "Associate GitHub Profile" in slack_response["actions"][0]["text"]


@pytest.mark.unit
def test_reconnect_command_existing_user(
    session, factory, generate_slash_command_request
):
    existing_user = "existing_user"
    github_user = factory.GitHubSummaryUser(slack_id=existing_user)
    install = github_user.configuration.slack_installation
    slack_user = factory.SlackUser(slack_id=existing_user, installation=install)
    data = generate_slash_command_request(
        "reconnect", user_id=existing_user, team_id=install.workspace_id
    )
    data["user"] = slack_user
    data["installation"] = install

    result = relink_github(**data)

    slack_response = result["attachments"][0]
    assert "Associate GitHub Profile" in slack_response["actions"][0]["text"]


@pytest.mark.unit
def test_disconnect_command_unregistered_user(
    session, factory, generate_slash_command_request
):
    github_summary_config = factory.GitHubSummaryConfiguration()
    install = github_summary_config.slack_installation
    slack_user = factory.SlackUser(slack_id="new_user", installation=install)
    data = generate_slash_command_request("disconnect", team_id=install.workspace_id)
    data["user"] = slack_user
    data["installation"] = install

    result = disconnect_github(**data)

    assert "No GitHub account associated with profile" in result["text"]


@pytest.mark.unit
def test_disconnect_command_registered_user(
    session, factory, generate_slash_command_request
):
    existing_user = "existing_user"
    github_user = factory.GitHubSummaryUser(slack_id=existing_user)
    install = github_user.configuration.slack_installation
    slack_user = factory.SlackUser(slack_id=existing_user, installation=install)
    data = generate_slash_command_request(
        "disconnect", user_id=github_user.slack_id, team_id=install.workspace_id
    )
    data["user"] = slack_user
    data["installation"] = install

    result = disconnect_github(**data)

    assert "Account has been deleted" in result["text"]
    assert not GitHubSummaryUser.query.get(github_user.id)


#########################
# Upcoming Event Schedule
#########################
@pytest.mark.end2end
def test_command_next(session, factory, generate_slash_command_request):
    group = factory.UpcomingEventsGroup()
    install = group.configuration.slack_installation
    factory.Event.create_batch(size=10, group=group)
    data = generate_slash_command_request("next", team_id=install.workspace_id)
    data["installation"] = install

    result = next_event(**data)

    assert result["response_type"] == "ephemeral"
    assert result["attachments"]
    assert not result["blocks"]
    assert not result["text"]


@pytest.mark.end2end
def test_command_events(session, factory, generate_slash_command_request):
    group = factory.UpcomingEventsGroup()
    install = group.configuration.slack_installation
    factory.Event.create_batch(size=10, group=group)
    data = generate_slash_command_request("events", team_id=install.workspace_id)
    data["installation"] = install

    result = upcoming_events(**data)

    assert result["response_type"] == "ephemeral"
    assert result["blocks"]
    assert not result["attachments"]
    assert not result["text"]
