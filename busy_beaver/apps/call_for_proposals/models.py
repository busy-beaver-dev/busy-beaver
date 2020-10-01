from finite_state_machine import StateMachine, transition
from finite_state_machine.exceptions import ConditionNotMet

from busy_beaver.common.models import BaseModel
from busy_beaver.exceptions import StateMachineError
from busy_beaver.extensions import db


def channel_selected(self):
    return self.config.channel is not None


class CallForProposalsEnabledStateMachine(StateMachine):
    initial_state = False

    def __init__(self, config):
        self.config = config
        self.state = config.enabled
        super().__init__()

    @transition(source=False, target=True, conditions=[channel_selected])
    def enable_call_for_proposals_feature(self):
        pass

    @transition(source=True, target=False)
    def disable_call_for_proposals_feature(self):
        pass

    def toggle(self):
        if self.state is True:
            self.disable_call_for_proposals_feature()
        else:
            self.enable_call_for_proposals_feature()


class CallForProposalsConfiguration(BaseModel):
    __tablename__ = "call_for_proposals_configuration"

    def __repr__(self):  # pragma: no cover
        return (
            f"<CallForProposalsConfiguration: {self.slack_installation.workspace_name}>"
        )

    enabled = db.Column(db.Boolean, default=False, nullable=False)
    installation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "slack_installation.id", name="fk_installation_id", ondelete="CASCADE"
        ),
        nullable=False,
    )
    channel = db.Column(db.String(20), nullable=False)
    internal_cfps = db.Column("internal_cfps", db.JSON)

    # Relationships
    slack_installation = db.relationship(
        "SlackInstallation", back_populates="cfp_config"
    )

    def toggle_configuration_enabled_status(self):
        machine = CallForProposalsEnabledStateMachine(self)
        try:
            machine.toggle()
        except ConditionNotMet as e:
            raise StateMachineError(f"Condition failed: {e.condition.__name__}")
        self.enabled = machine.state
