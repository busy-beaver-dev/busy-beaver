from dateutil.parser import parse
from transitions import Machine

from busy_beaver.extensions import db
from busy_beaver.apps.external_integrations.workflow import (
    save_configuration,
    send_configuration_message,
    send_welcome_message,
)
from busy_beaver.models import SlackInstallation


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
            source="installed",
            dest="user_welcomed",
            before="send_installing_user_welcome_message",
            after="update_state_in_database",
        )
        self.machine.add_transition(
            trigger="advance",
            source="user_welcomed",
            dest="config_requested",
            before="send_initial_configuration_request",
            after="update_state_in_database",
            conditions="check_channel_membership",
        )
        self.machine.add_transition(
            trigger="advance",
            source="config_requested",
            dest="active",
            before="save_configuration_to_database",
            after="update_state_in_database",
            conditions="validate_configuration",
        )
        self.machine.add_transition(
            trigger="advance",
            source="active",
            dest="active",
            after="update_state_in_database",
        )

    def send_installing_user_welcome_message(self):
        send_welcome_message(self.slack_installation)

    def send_initial_configuration_request(self):
        send_configuration_message(self.slack_installation)

    def save_configuration_to_database(self):
        save_configuration(self.slack_installation, time_to_post=self.payload)

    def update_state_in_database(self):
        self.slack_installation.state = self.state
        db.session.add(self.slack_installation)
        db.session.commit()

    def check_channel_membership(self):
        if not self.slack_installation.github_summary_config:
            send_welcome_message(self.slack_installation)
            return False
        return True

    def validate_configuration(self):
        try:
            self.payload = parse(self.payload).time()
        except (ValueError, TypeError):
            send_configuration_message(self.slack_installation)
            return False
        return True
