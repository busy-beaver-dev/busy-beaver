from flask_wtf import FlaskForm
from wtforms.fields import FieldList, FormField, SelectField, StringField
from wtforms.fields.html5 import URLField
from wtforms.validators import URL, DataRequired


class InternalCFPItemForm(FlaskForm):
    class Meta:
        csrf = False  # this form is only used as a subform

    event = StringField(validators=[DataRequired()])
    url = URLField("CFP URL", validators=[URL()])


class CFPSettingsForm(FlaskForm):
    channel = SelectField(label="Channel")
    internal_cfps = FieldList(
        FormField(InternalCFPItemForm), min_entries=0, max_entries=10
    )


class TemplateInternalCFPForm(FlaskForm):
    internal_cfps = FieldList(
        FormField(InternalCFPItemForm), min_entries=1, max_entries=1
    )
