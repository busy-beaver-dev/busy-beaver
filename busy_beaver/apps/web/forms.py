from flask_wtf import FlaskForm
import pytz
from wtforms.fields import SelectField
from wtforms.validators import DataRequired
from wtforms_components import TimeField

from busy_beaver.common.datetime_utilities import add_gmt_offset_to_timezone

TIMEZONES = [(pytz.timezone(tz), tz) for tz in pytz.common_timezones]
TZ_CHOICES = sorted(
    add_gmt_offset_to_timezone(TIMEZONES), key=lambda x: int(x[1][3:5]), reverse=True
)


class GitHubSummaryConfigurationForm(FlaskForm):
    channel = SelectField(label="Channel")

    summary_post_time = TimeField(
        "When to post GitHub Summary?", validators=[DataRequired()]
    )
    summary_post_timezone = SelectField(
        label="Timezone", choices=TZ_CHOICES, default="UTC"
    )
