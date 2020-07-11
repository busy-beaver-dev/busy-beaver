from finite_state_machine import StateMachine, transition
from finite_state_machine.exceptions import ConditionNotMet
from sqlalchemy_utils import TimezoneType

from busy_beaver.common.models import BaseModel
from busy_beaver.exceptions import StateMachineError
from busy_beaver.extensions import db


def time_to_post_has_been_configured(self):
    return self.config.summary_post_time and self.config.summary_post_timezone


class GitHubConfigEnabledStateMachine(StateMachine):
    initial_state = False

    def __init__(self, config):
        self.config = config
        self.state = config.enabled
        super().__init__()

    @transition(
        source=False, target=True, conditions=[time_to_post_has_been_configured]
    )
    def enable_github_summary_feature(self):
        pass

    @transition(source=True, target=False)
    def disable_github_summary_feature(self):
        pass

    def toggle(self):
        if self.state:
            self.disable_github_summary_feature()
        else:
            self.enable_github_summary_feature()


class GitHubSummaryConfiguration(BaseModel):
    __tablename__ = "github_summary_configuration"

    def __repr__(self):  # pragma: no cover
        return f"<GitHubSummaryConfiguration: {self.slack_installation.workspace_name}>"

    enabled = db.Column(db.Boolean, default=False, nullable=False)
    installation_id = db.Column(
        db.Integer,
        db.ForeignKey("slack_installation.id", name="fk_installation_id"),
        nullable=False,
    )
    channel = db.Column(db.String(20), nullable=False)
    summary_post_time = db.Column(db.Time, nullable=True)
    summary_post_timezone = db.Column(TimezoneType(backend="pytz"), nullable=True)

    # Relationships
    slack_installation = db.relationship(
        "SlackInstallation", back_populates="github_summary_config"  # , lazy="joined"
    )
    github_summary_users = db.relationship(
        "GitHubSummaryUser", back_populates="configuration"
    )

    def toggle_configuration_enabled_status(self):
        machine = GitHubConfigEnabledStateMachine(self)
        try:
            machine.toggle()
        except ConditionNotMet as e:
            raise StateMachineError(f"Condition failed: {e.condition.__name__}")
        self.enabled = machine.state


class GitHubSummaryUser(BaseModel):

    __tablename__ = "github_summary_user"

    def __repr__(self):  # pragma: no cover
        return f"<User slack: {self.slack_id} github: {self.github_username}>"

    # Attributes
    config_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "github_summary_configuration.id", name="fk_github_summary_configuration_id"
        ),
        nullable=False,
    )
    slack_id = db.Column(db.String(300), nullable=False)
    github_id = db.Column(db.String(300), nullable=True)
    github_username = db.Column(db.String(300), nullable=True)
    github_state = db.Column(db.String(36), nullable=True)
    github_access_token = db.Column(db.String(100), nullable=True)

    # Relationships
    configuration = db.relationship(
        "GitHubSummaryConfiguration", back_populates="github_summary_users"
    )
