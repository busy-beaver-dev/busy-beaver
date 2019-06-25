import factory
from busy_beaver.models import SlackInstallation as model


def SlackInstallation(session):
    class _SlackInstallationFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        access_token = factory.Faker("uuid4")
        authorizing_user_id = "abc"

        bot_access_token = factory.Faker("uuid4")
        bot_user_id = "def"

        scope = "identity chat:message:write"
        workspace_id = "SC234sdfsde"
        workspace_name = "ChiPy"

    return _SlackInstallationFactory
