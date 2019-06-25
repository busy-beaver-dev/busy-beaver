import factory
from .slack import SlackInstallation
from busy_beaver.models import (
    ApiUser as api_user_model,
    GitHubSummaryUser as github_summary_model,
)


def ApiUser(session):
    class _ApiUserFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = api_user_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        username = "test_api_user"
        token = "abcd"
        role = "user"

    return _ApiUserFactory


def GitHubSummaryUser(session):
    class _GitHubSummaryUserFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = github_summary_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        slack_id = "slack_user"
        github_id = "13242345435"
        github_username = "github_user"
        github_state = ""
        github_access_token = factory.Faker("uuid4")
        installation = factory.SubFactory(SlackInstallation(session))

    return _GitHubSummaryUserFactory
