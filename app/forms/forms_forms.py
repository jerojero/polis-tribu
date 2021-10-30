from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms import IntegerField, SelectField
from wtforms import RadioField, TextAreaField
from wtforms import FormField, FieldList
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired, Optional, NumberRange
from wtforms.validators import Regexp, ValidationError
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


class ContactForm(MyBaseForm):

    special_form = True

    contact_method = SelectField(
        "Método de contacto",
        choices=[('phone', 'Llamada Telefónica'),
                 ('email', 'Correo electrónico'),
                 ('wsp', 'WhatsApp'),
                 ('any', 'Cualquiera')],
        validators=[DataRequired()])
    next = SubmitField("Siguiente")


class PaymentForm(MyBaseForm):

    special_form = True

    name = StringField("Nombre", validators=[DataRequired()])
    last_name = StringField("Apellido", validators=[DataRequired()])
    rut = StringField("Rut", validators=[DataRequired()],
                      description="Ej: 99999999k")
    bank = StringField("Banco", validators=[DataRequired()])
    account = SelectField(
        "Cuenta",
        choices=[('vista', 'Cuenta Vista'),
                 ('rut', 'Cuenta Rut'),
                 ('corriente', 'Cuenta Corriente')],
        validators=[DataRequired()])
    account_number = StringField(
        "Numero de cuenta", validators=[DataRequired()])
    third_party = BooleanField(
        "Si los datos que he entregado no son de mi persona entonces autorizo que se haga el pago a un tercero.")
    next = SubmitField("Siguiente")

    def validate_rut(self, rut):
        rut = rut.data
        if not rut.isalnum():
            raise ValidationError('Rut debe ser sin puntos ni guiones.')
        if (len(rut) < 8) or (len(rut) > 9):
            raise ValidationError('Rut debe contener entre 8 y 9 digitos.')
        if not rut[:-1].isdigit():
            raise ValidationError('Rut es inválido.')
        if not (rut[-1].isdigit() or rut[-1] == 'k'):
            raise ValidationError('Rut es inválido.')


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
            validators = [DataRequired(message="Debe ingresar un número."),
                          NumberRange(message="Debe ingresar un número")]
        else:
            validators = [Optional(), NumberRange()]
        form = IntegerField(
            label=title, validators=validators, default=default)
        return (f"question_{question.id}", form)

    elif question.question_type == "rk":
        title = question.title
        if not question.optional:
            title = title + ' (*)'
            validators = [DataRequired("Debe ingresar una opción.")]
        else:
            validators = [Optional()]
        choices = [(x, str(x)) for x in range(11)]
        choices = choices + [('ns', 'No sabe'), ('nr', 'No responde')]
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

    elif question.question_type == "fc":
        return ContactForm

    elif question.question_type == "fp":
        return PaymentForm

    else:
        return None
