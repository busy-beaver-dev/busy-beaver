from finite_state_machine.exceptions import ConditionNotMet
import pytest
from sqlalchemy.exc import IntegrityError

from busy_beaver.apps.upcoming_events.models import PostCRONEnabledStateMachine


def test_meetup_group_configuration_unique_constraint(factory):
    group = factory.UpcomingEventsGroup(meetup_urlname="_ChiPy_")

    with pytest.raises(IntegrityError):
        factory.UpcomingEventsGroup(
            meetup_urlname="_ChiPy_", configuration=group.configuration
        )


def test_cron_job_field_cannot_be_enabled_if_no_channel_is_selected(factory):
    config = factory.UpcomingEventsConfiguration(channel=None, post_cron_enabled=False)

    machine = PostCRONEnabledStateMachine(config)

    with pytest.raises(ConditionNotMet):
        machine.toggle()
