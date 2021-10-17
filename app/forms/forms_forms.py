from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms import IntegerField, SelectField
from wtforms import RadioField, TextAreaField
from wtforms import FormField, FieldList
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired, Optional, InputRequired, Required
from app.models import Results
from flask import current_app


class MyBaseForm(FlaskForm):
    class Meta:
        locales = ['es_ES', 'es']


class SelectForm(MyBaseForm):
    select = SelectField("Placeholder", choices=[])


class SelectFormList(SelectForm):
    select_entries = FieldList(FormField(SelectForm))


class AddQuestionForm(MyBaseForm):
    question_type = SelectField("Question type:", choices=[(
        "hd", "Header"), ("mc", "Multiple choice"),
        ("rk", "Ranked"), ("st", "String")],
        validators=[DataRequired()])
    title = TextAreaField("Title of question", validators=[DataRequired()])
    description = TextAreaField("Description if necessary")
    section = IntegerField()
    optional = BooleanField("Check if question is optional")
    tail = BooleanField("Check if last question")
    submit = SubmitField('Submit Question')


class AddAnswerForm(MyBaseForm):
    text = StringField("Text of answer", validators=[DataRequired()])
    associated_question = IntegerField(
        "Associated question", validators=[DataRequired()])
    next_question = IntegerField("If there is a special next question")
    submit = SubmitField("Submit Answer")


class LinkQuestionsForm(MyBaseForm):
    previous_question = IntegerField(
        "Previous question", validators=[DataRequired()])
    next_question = IntegerField("Next question", validators=[DataRequired()])
    submit = SubmitField("Link both questions")


def create_questionaire(fields_list):
    class MultipleChoice(MyBaseForm):
        pass
    cls = MultipleChoice
    for fields in fields_list:
        setattr(cls, *fields)
    return cls


def make_question_form(question, user):
    default = None
    result = Results.query.get(int(f"{user.id}00{question.id}"))
    if result:
        default = result.answers

    if question.question_type == "hd":
        return None

    elif question.question_type == "mc":
        title = question.title
        answers = question.answer.all()
        choices = [(answer.id, answer.text) for answer in answers]
        if not question.optional:
            title = title + ' (*)'
            validators = DataRequired("Debe ingresar una opción.")
        else:
            validators = Optional()
        form = RadioField(label=title, choices=choices,
                          validators=[validators], default=default,
                          render_kw={'class': 'vertical'})
        return (f"question_{question.id}", form)

    elif question.question_type == "st":
        title = question.title
        if not question.optional:
            title = title + ' (*)'
            validators = DataRequired(message="Debe completar la pregunta.")
        else:
            validators = Optional()
        form = StringField(label=title, validators=[
                           validators], default=default)
        return (f"question_{question.id}", form)

    elif question.question_type == "rk":
        title = question.title
        if not question.optional:
            title = title + ' (*)'
            validators = [DataRequired("Debe ingresar una opción.")]
        else:
            validators = [Optional()]
        choices = [(x, str(x)) for x in range(11)]
        # if default:
        #     current_app.logger.info("default")
        #     form = IntegerRangeField(label=title,
        #                              default=default,
        #                              render_kw={'min': '0',
        #                                         'max': '10', 'step': '1',
        #                                         'class': f'{question.id}',
        #                                         'default_text': default,
        #                                         'oninput': f'outputUpdate(value, "output{question.id}")'})
        # else:
        #     current_app.logger.info(f"no default {validators}")
        #     form = IntegerRangeField(label=title,
        #                              # default="hello",
        #                              render_kw={'min': '0',
        #                                         'max': '10', 'step': '1',
        #                                         'class': f'{question.id}',
        #                                         'default_text': 5,
        #                                         'oninput': f'outputUpdate(value, "output{question.id}")'},
        #                              validators=validators,)
        form = RadioField(label=title, choices=choices,
                          validators=validators, default=default, render_kw={'class': 'horizontal'})
        return (f"question_{question.id}", form)

    else:
        return None
