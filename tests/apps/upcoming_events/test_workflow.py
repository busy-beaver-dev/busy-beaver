from busy_beaver.apps.upcoming_events.workflow import add_new_group_to_configuration
from busy_beaver.models import UpcomingEventsConfiguration, UpcomingEventsGroup


class TestUpdateSettings:
    def test_add_new_group_to_configuration(self, factory):
        """Happy Path"""
        config = factory.UpcomingEventsConfiguration()

        add_new_group_to_configuration(
            installation=config.slack_installation,
            upcoming_events_config=config,
            meetup_urlname="_ChiPy_",
        )

        groups = UpcomingEventsGroup.query.all()
        assert len(groups) == 1
        group_added = groups[0]
        assert group_added.meetup_urlname == "_ChiPy_"

    def test_add_new_group_to_configuration_when_config_does_not_exist(self, factory):
        """Workflow:
        - User tries to add a group when the config doesn't exist
        - Program creates config
        - Adds group to new config"""
        installation = factory.SlackInstallation()

        add_new_group_to_configuration(
            installation=installation,
            upcoming_events_config=None,
            meetup_urlname="_ChiPy_",
        )

        groups = UpcomingEventsGroup.query.all()
        assert len(groups) == 1
        group_added = groups[0]
        assert group_added.meetup_urlname == "_ChiPy_"

        # check group and config are linked
        configs = UpcomingEventsConfiguration.query.all()
        assert len(configs) == 1
        config = configs[0]
        assert group_added.configuration is config
