import pytest

from busy_beaver.adapters.meetup import EventDetails
from busy_beaver.blueprints.integration.slack.slash_command import (
    command_not_found,
    disconnect_github,
    display_help_text,
    link_github,
    next_event,
    relink_github,
)
from busy_beaver.models import User

MODULE_TO_TEST = "busy_beaver.blueprints.integration.slack.slash_command"


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

    response = client.post("/slack-slash-commands", headers=headers, data=data)

    assert response.status_code == 200
    assert "/busybeaver help" in response.json["text"].lower()


@pytest.mark.integration
def test_slack_command_invalid_command(
    client, create_slack_headers, generate_slash_command_request
):
    data = generate_slash_command_request("non-existent")
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack-slash-commands", headers=headers, data=data)

    assert response.status_code == 200
    assert "command not found" in response.json["text"].lower()


@pytest.mark.integration
def test_slack_command_empty_command(
    client, create_slack_headers, generate_slash_command_request
):
    data = generate_slash_command_request(command="")
    headers = create_slack_headers(100_000_000, data, is_json_data=False)

    response = client.post("/slack-slash-commands", headers=headers, data=data)

    assert response.status_code == 200
    assert "/busybeaver help" in response.json["text"].lower()


#########################
# Upcoming Event Schedule
#########################
@pytest.fixture
def patched_meetup(mocker, patcher):
    class FakeMeetupClient:
        def __init__(self, *, events):
            self.mock = mocker.MagicMock()
            if events:
                self.events = events

        def get_events(self, *args, **kwargs):
            self.mock(*args, **kwargs)
            return self.events

        def __repr__(self):
            return "<FakeMeetupClient>"

    def _wrapper(*, events=None):
        obj = FakeMeetupClient(events=events)
        return patcher(MODULE_TO_TEST, namespace="meetup", replacement=obj)

    return _wrapper


@pytest.mark.unit
def test_command_next_event(generate_slash_command_request, patched_meetup):
    data = generate_slash_command_request("next")
    patched_meetup(
        events=[
            EventDetails(
                name="ChiPy",
                url="http://meetup.com/_ChiPy_/event/blah",
                dt=1_557_959_400_000,
                venue="Numerator",
            )
        ]
    )

    result = next_event(**data)

    slack_response = result.json["attachments"][0]
    assert "ChiPy" in slack_response["title"]
    assert "http://meetup.com/_ChiPy_/event/blah" in slack_response["title_link"]
    assert "Numerator" in slack_response["text"]


# TODO with the way we changed this, it makes sense to do this the meetup adapter test
@pytest.mark.unit
def test_command_next_event_location_not_set(
    generate_slash_command_request, patched_meetup
):
    data = generate_slash_command_request("next")
    patched_meetup(
        events=[
            EventDetails(
                name="ChiPy",
                url="http://meetup.com/_ChiPy_/event/blah",
                dt=1_557_959_400_000,
                venue="TBD",
            )
        ]
    )

    result = next_event(**data)

    slack_response = result.json["attachments"][0]
    assert "ChiPy" in slack_response["title"]
    assert "http://meetup.com/_ChiPy_/event/blah" in slack_response["title_link"]
    assert "TBD" in slack_response["text"]


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
