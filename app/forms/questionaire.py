from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms import IntegerField, SelectField
from wtforms import FieldList, FormField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Lxs400


class BaseForm(FlaskForm):
    class Meta:
        locales = ['es_ES', 'es']


def create_questionaire(fields_list):
    class MultipleChoice(BaseForm):
        pass
    cls = MultipleChoice
    for fields in fields_list:
        setattr(cls, *fields)
    return cls
