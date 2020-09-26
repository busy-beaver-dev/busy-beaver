from flask_wtf import FlaskForm
from wtforms.fields import FieldList, FormField, SelectField, StringField
from wtforms.fields.html5 import URLField
from wtforms.validators import URL, DataRequired
from wtforms.widgets import HTMLString, html_params


class RemoveButtonWidget(object):
    input_type = "submit"

    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", "button")
        if "value" not in kwargs:
            kwargs["value"] = field._value()

        kwargs["class"] = "remove form-control"
        return HTMLString(
            "<button {params}>{label}</button>".format(
                params=self.html_params(name=field.name, **kwargs), label="X"
            )
        )


class RemoveButtonField(StringField):
    widget = RemoveButtonWidget()


class InternalCFPItemForm(FlaskForm):
    class Meta:
        csrf = False  # this form is only used as a subform

    event = StringField(validators=[DataRequired()])
    url = URLField("CFP URL", validators=[URL()])
    remove = RemoveButtonField("remove")


class CFPSettingsForm(FlaskForm):
    channel = SelectField(label="Channel")
    internal_cfps = FieldList(
        FormField(InternalCFPItemForm), min_entries=0, max_entries=10
    )


class TemplateInternalCFPForm(FlaskForm):
    internal_cfps = FieldList(
        FormField(InternalCFPItemForm), min_entries=1, max_entries=1
    )
