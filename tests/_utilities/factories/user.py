import factory
from .slack import SlackInstallationFactory
from busy_beaver.models import ApiUser, GitHubSummaryUser


def ApiUserFactory(session):
    class _ApiUserFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = ApiUser
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        username = "test_api_user"
        token = "abcd"
        role = "user"

    return _ApiUserFactory


def GitHubSummaryUserFactory(session):
    class _GitHubSummaryUserFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = GitHubSummaryUser
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        slack_id = "slack_user"
        github_id = "13242345435"
        github_username = "github_user"
        github_state = ""
        github_access_token = factory.Faker("uuid4")
        installation = factory.SubFactory(SlackInstallationFactory(session))

    return _GitHubSummaryUserFactory
