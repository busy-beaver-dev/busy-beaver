import factory
from busy_beaver.models import SlackInstallation


class SlackInstallationFactory(factory.Factory):
    class Meta:
        model = SlackInstallation

    access_token = factory.Faker("uuid4")
    authorizing_user_id = "abc"

    bot_access_token = factory.Faker("uuid4")
    bot_user_id = "def"

    scope = "identity chat:message:write"
    workspace_id = "SC234sdfsde"
    workspace_name = "ChiPy"
