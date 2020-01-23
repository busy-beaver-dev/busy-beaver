import pytest


@pytest.fixture
def generate_slash_command_request():
    def _generate_data(
        command,
        user_id="U5FRZAD323",
        team_id="T5GCMNWAFSDFSDF",
        channel_id="CFLDRNBSDFD",
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
