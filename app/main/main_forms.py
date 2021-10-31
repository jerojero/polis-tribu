from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms import IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Lxs400


class MyBaseForm(FlaskForm):
    class Meta:
        locales = ['es_ES', 'es']


class EmailForm(MyBaseForm):
    csv = StringField('Nombre del archivo con base de datos',
                      render_kw={'placeholder': "pruebas"})
    title = StringField('Titulo del email',
                        render_kw={'placeholder':
                                   "[Consulta Salud] - Email de Registro"})
    body = StringField('Nombre del email',
                       render_kw={'placeholder':
                                  "codigos"})
    submit = SubmitField('Enviar')


class DownloadForm(MyBaseForm):
    download = SelectField('Nombre de la base de datos a descargar:',
                           choices=[('email', 'Seguimiento de email'),
                                    ('responsesx', 'Respuestas de la encuesta (lxs400)'),
                                    ('responsesd', 'Respuestas de la encuesta (doctores)'),
                                    ('questions', 'Codigos de las preguntas'),
                                    ('notcompleted', 'Gente que no ha completado encuesta'),
                                    ('notreg', 'Gente no registrada')],
                           validators=[DataRequired()])
    submit = SubmitField('Descargar')
