from . import BaseModel
from busy_beaver.extensions import db


class GitHubSummaryConfiguration(BaseModel):
    __tablename__ = "github_summary_configuration"

    def __repr__(self):  # pragma: no cover
        return f"<GitHubSummaryConfiguration>"

    installation_id = db.Column(
        db.Integer,
        db.ForeignKey("slack_installation.id", name="fk_installation_id"),
        nullable=False,
    )
    channel = db.Column(db.String(20), nullable=False)
    time_to_post = db.Column(db.String(20), nullable=True)
    timezone_info = db.Column(db.JSON)

    # Relationships
    slack_installation = db.relationship(
        "SlackInstallation", back_populates="github_summary_config"
    )


class GitHubSummaryUser(BaseModel):
    """GitHub Summary User table

    TODO: GitHubSummaryUser should really be related to
    GitHubSummaryConfiguration versus SlackInstallation
    """

    __tablename__ = "github_summary_user"

    def __repr__(self):  # pragma: no cover
        return f"<User slack: {self.slack_id} github: {self.github_username}>"

    # Attributes
    installation_id = db.Column(
        db.Integer,
        db.ForeignKey("slack_installation.id", name="fk_installation_id"),
        nullable=False,
    )
    slack_id = db.Column(db.String(300), nullable=False)
    github_id = db.Column(db.String(300), nullable=True)
    github_username = db.Column(db.String(300), nullable=True)
    github_state = db.Column(db.String(36), nullable=True)
    github_access_token = db.Column(db.String(100), nullable=True)

    # Relationships
    installation = db.relationship(
        "SlackInstallation", back_populates="github_summary_users"
    )
