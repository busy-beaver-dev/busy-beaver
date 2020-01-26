import factory

from busy_beaver.models import ApiUser as api_user_model


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
