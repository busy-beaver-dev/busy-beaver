import factory
from busy_beaver.models import ApiUser


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
