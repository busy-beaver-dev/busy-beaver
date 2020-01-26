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
        installation = factory.SubFactory(SlackInstallation(session))

    return _GitHubSummaryUserFactory


def GitHubSummaryConfiguration(session):
    class _GitHubSummaryConfiguration(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = github_summary_configuration_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        channel = "busy-beaver"
        time_to_post = "2:00pm"
        timezone_info = {}
        slack_installation = factory.SubFactory(SlackInstallation(session))

    return _GitHubSummaryConfiguration
