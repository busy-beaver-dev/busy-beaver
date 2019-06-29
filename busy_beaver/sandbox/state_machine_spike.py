from transitions import Machine

from busy_beaver.extensions import db
from busy_beaver.apps.external_integrations.workflow import send_welcome_message
from busy_beaver.models import SlackInstallation


class OnboardUserWorkflow:

    STATES = ["installed", "user_welcomed", "config_requested", "actve"]

    def __init__(self, slack_installation: SlackInstallation):
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
        )
        self.machine.add_transition(
            trigger="advance",
            source="config_requested",
            dest="active",
            before="save_configuration_to_database",
            after="update_state_in_database",
        )

    def send_installing_user_welcome_message(self):
        send_welcome_message(self.slack_installation)

    def send_initial_configuration_request(self):
        pass

    def save_configuration_to_database(self):
        """This feels implicit; once we get this back, we kick off the state machine"""
        # maybe have a self.payload = None and then if something is there add it

    def update_state_in_database(self):
        self.slack_installation.state = self.state
        db.session.add(self.slack_installation)
        db.session.commit()


if __name__ == "__main__":
    s = SlackInstallation.query.first()
    s.state = "installed"
    db.session.add(s)
    db.session.commit()
    workflow = OnboardUserWorkflow(s)
    workflow.advance()
