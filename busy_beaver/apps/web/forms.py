from flask_login import current_user
from flask_wtf import FlaskForm
import pytz
from wtforms import ValidationError
from wtforms.fields import IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, NumberRange
from wtforms_components import TimeField

from busy_beaver.clients import meetup
from busy_beaver.common.datetime_utilities import add_gmt_offset_to_timezone
from busy_beaver.models import UpcomingEventsGroup

TIMEZONES = [(pytz.timezone(tz), tz) for tz in pytz.common_timezones]
TZ_CHOICES = sorted(
    add_gmt_offset_to_timezone(TIMEZONES), key=lambda x: int(x[1][3:5]), reverse=True
)
WEEKDAYS = [
    ("Sunday",) * 2,
    ("Monday",) * 2,
    ("Tuesday",) * 2,
    ("Wednesday",) * 2,
    ("Thursday",) * 2,
    ("Friday",) * 2,
    ("Saturday",) * 2,
]


class GitHubSummaryConfigurationForm(FlaskForm):
    channel = SelectField(label="Channel")

    summary_post_time = TimeField("Time to post", validators=[DataRequired()])
    summary_post_timezone = SelectField(
        label="Timezone", choices=TZ_CHOICES, default="UTC"
    )


class UpcomingEventsConfigurationForm(FlaskForm):
    channel = SelectField(label="Channel")

    post_day_of_week = SelectField("Day to post", choices=WEEKDAYS, default="Monday")
    post_time = TimeField("Time to post", validators=[DataRequired()])
    post_timezone = SelectField(label="Timezone", choices=TZ_CHOICES, default="UTC")
    post_num_events = IntegerField(
        label="Number of messages to post", validators=[NumberRange(min=1)]
    )


class AddNewGroupConfigurationForm(FlaskForm):
    meetup_urlname = StringField("Unique URL identifer", validators=[DataRequired()])

    def validate_meetup_urlname(form, field):
        group_to_add = field.data

        matching_group = (
            UpcomingEventsGroup.query.filter(
                UpcomingEventsGroup.meetup_urlname.ilike(group_to_add)
            )
            .filter_by(configuration=current_user.installation.upcoming_events_config)
            .first()
        )
        if matching_group:
            raise ValidationError("Group already added")

        group_name = meetup.get_urlname(group_to_add)
        if not group_name:
            raise ValidationError("Group does not exist")

        field.data = group_name
