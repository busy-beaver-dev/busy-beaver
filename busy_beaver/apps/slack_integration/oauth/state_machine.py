from finite_state_machine import StateMachine, transition
from transitions import Machine

from busy_beaver.apps.slack_integration.oauth.workflow import (
    save_configuration,
    send_configuration_message,
    send_welcome_message,
)
from busy_beaver.extensions import db
from busy_beaver.models import SlackInstallation


def no_github_summary_configuration(self):
    return self.slack_installation.github_summary_config is None


def has_github_summary_configuration(self):
    return self.slack_installation.github_summary_config is not None


class SlackInstallationOnboardUserStateMachine(StateMachine):
    initial_state = "installed"

    def __init__(self, slack_installation):
        self.state = slack_installation.state
        self.slack_installation = slack_installation
        super().__init__()

    @transition(source="installed", target="user_welcomed")
    def welcome_user(self):
        send_welcome_message(self.slack_installation)

    @transition(
        source="user_welcomed",
        target="config_requested",
        conditions=[no_github_summary_configuration],
    )
    def send_initial_configuration_request(self, channel):
        send_configuration_message(self.slack_installation, channel)

    @transition(
        source=["config_requested", "active"],
        target="active",
        conditions=[has_github_summary_configuration],
    )
    def save_configuration_to_database(
        self, summary_post_time, summary_post_timezone, slack_id
    ):
        save_configuration(
            self.slack_installation,
            time_to_post=summary_post_time,
            timezone_to_post=summary_post_timezone,
            slack_id=slack_id,
        )

    @transition(source="active", target="active")
    def update_state_in_database(self):
        pass


class SlackInstallationOnboardUserWorkflow:

    STATES = ["installed", "user_welcomed", "config_requested", "active"]

    def __init__(self, slack_installation: SlackInstallation, payload: dict = None):
        self.payload = payload
        self.slack_installation = slack_installation
        self.machine = Machine(
            model=self, states=self.__class__.STATES, initial=slack_installation.state
        )

        self.machine.add_transition(
            trigger="advance",
            source="active",
            dest="active",
            after="update_state_in_database",
        )

    def update_state_in_database(self):
        self.slack_installation.state = self.state
        db.session.add(self.slack_installation)
        db.session.commit()
