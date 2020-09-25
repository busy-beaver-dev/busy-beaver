import factory

from .slack import SlackInstallation
from busy_beaver.models import CallForProposalsConfiguration as cfp_config_model


def CallForProposalsConfiguration(session):
    class _CFPConfigFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = cfp_config_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        enabled = True
        slack_installation = factory.SubFactory(SlackInstallation(session))
        channel = "call-for-proposals"
        internal_cfps = [
            {"event": "`__main__` Meeting", "url": "http://bit.ly/chipy-cfp"},
            {"event": "Special Interest Groups", "url": "http://bit.ly/chipy-sig-cfp"},
        ]

    return _CFPConfigFactory
