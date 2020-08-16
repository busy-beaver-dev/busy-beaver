import pytest
from sqlalchemy.exc import IntegrityError


def test_meetup_group_configuration_unique_constraint(factory):
    group = factory.UpcomingEventsGroup(meetup_urlname="_ChiPy_")

    with pytest.raises(IntegrityError):
        factory.UpcomingEventsGroup(
            meetup_urlname="_ChiPy_", configuration=group.configuration
        )
