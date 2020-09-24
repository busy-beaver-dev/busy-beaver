from flask_wtf import FlaskForm, Form
from wtforms.fields import FieldList, FormField, SelectField, StringField
from wtforms.fields.html5 import URLField
from wtforms.validators import URL, DataRequired


class InternalCFPItemForm(Form):
    event = StringField(validators=[DataRequired()])
    url = URLField("CFP URL", validators=[URL()])


class CFPSettingsForm(FlaskForm):
    channel = SelectField(label="Channel")
    internal_cfps = FieldList(
        FormField(InternalCFPItemForm), min_entries=1, max_entries=10
    )
