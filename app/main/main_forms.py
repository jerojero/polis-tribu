from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import SelectField, BooleanField
from wtforms.validators import DataRequired


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
    todos = BooleanField('Todos')
    submit = SubmitField('Enviar')


class DownloadForm(MyBaseForm):
    download = SelectField('Nombre de la base de datos a descargar:',
                           choices=[('email', 'Seguimiento de email'),
                                    ('payment', 'Datos para pago'),
                                    ('responsesx',
                                     'Respuestas de la encuesta (lxs400)'),
                                    ('responsesd',
                                     'Respuestas de la encuesta (doctores)'),
                                    ('questions', 'Codigos de las preguntas'),
                                    ('notcompleted',
                                     'Gente que no ha completado encuesta'),
                                    ('notreg', 'Gente no registrada')],
                           validators=[DataRequired()])
    submit = SubmitField('Descargar')
