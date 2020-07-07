from datetime import time

import factory

from .slack import SlackInstallation
from busy_beaver.models import (
    GitHubSummaryConfiguration as github_summary_configuration_model,
)
from busy_beaver.models import GitHubSummaryUser as github_summary_user_model


def GitHubSummaryUser(session):
    class _GitHubSummaryUserFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = github_summary_user_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        slack_id = "slack_user"
        github_id = "13242345435"
        github_username = "github_user"
        github_state = ""
        github_access_token = factory.Faker("uuid4")
        configuration = factory.SubFactory(GitHubSummaryConfiguration(session))

    return _GitHubSummaryUserFactory


def GitHubSummaryConfiguration(session):
    class _GitHubSummaryConfiguration(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = github_summary_configuration_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        channel = "busy-beaver"
        summary_post_time = time(14, 00)
        summary_post_timezone = "America/Chicago"
        slack_installation = factory.SubFactory(SlackInstallation(session))

    return _GitHubSummaryConfiguration
