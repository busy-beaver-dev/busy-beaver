from sqlalchemy_utils import TimezoneType

from busy_beaver.common.models import BaseModel
from busy_beaver.extensions import db


class GitHubSummaryConfiguration(BaseModel):
    __tablename__ = "github_summary_configuration"

    def __repr__(self):  # pragma: no cover
        return f"<GitHubSummaryConfiguration: {self.slack_installation.workspace_name}>"

    installation_id = db.Column(
        db.Integer,
        db.ForeignKey("slack_installation.id", name="fk_installation_id"),
        nullable=False,
    )
    channel = db.Column(db.String(20), nullable=False)
    time_to_post = db.Column(db.String(20), nullable=True)
    timezone_info = db.Column(db.JSON)
    summary_post_time = db.Column(db.Time, nullable=True)
    summary_post_timezone = db.Column(TimezoneType(backend="pytz"), nullable=True)

    # Relationships
    slack_installation = db.relationship(
        "SlackInstallation", back_populates="github_summary_config"
    )
    github_summary_users = db.relationship(
        "GitHubSummaryUser", back_populates="configuration"
    )


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
