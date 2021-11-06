from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms import IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Lxs400


class MyBaseForm(FlaskForm):
    class Meta:
        locales = ['es_ES', 'es']


class LoginForm(MyBaseForm):
    username = StringField('Nombre de usuario o correo electrónico',
                           validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Inicia sesión')


class RegistrationForm(MyBaseForm, FlaskForm):
    username = StringField('Nombre de usuario para esta plataforma (*)',
                           validators=[DataRequired()])
    name = StringField('Nombre (*)',
                       validators=[DataRequired()],
                       description="Ej: Juan")
    last_name = StringField('Apellido (*)',
                            validators=[DataRequired()],
                            description="Ej: Pérez")
    email = StringField('Correo electrónico (*)',
                        validators=[DataRequired(), Email()],
                        description="Ej: alex@ejemplo.com")
    email2 = StringField('Repetir correo electrónico (*)',
                         validators=[DataRequired(), EqualTo('email')])
    phone = StringField('Numero de teléfono (*)',
                        validators=[DataRequired()],
                        description="Ej: +569xxxxxxxx")
    password = PasswordField('Crear contraseña para esta plataforma (*)',
                             validators=[DataRequired()])
    password2 = PasswordField('Repetir contraseña (*)',
                              validators=[DataRequired(), EqualTo('password')])
    verification_code = StringField('Codigo de verificación (*)',
                                    validators=[DataRequired()])
    consent_bool = BooleanField("He leído y acepto los términos y condiciones de uso de la plataforma",
                                validators=[DataRequired()])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        username_norm = username.data.lower()
        user = User.query.filter_by(username=username_norm).first()
        if user is not None:
            raise ValidationError('Este nombre de usuario ya está registrado.'
                                  ' Porfavor elegir otro'
                                  ' nombre de usuario')
        if not username.data.isalnum():
            raise ValidationError('Solo letras y números para '
                                  'el nombre de usuario.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Este correo electrónico ya está siendo '
                                  'utilizado. Por favor use otra dirección de '
                                  'correo electrónico.')

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

    def validate_verification_code(self, verification_code):
        vf = verification_code.data.replace(" ", "")
        lxs400 = Lxs400.query.filter_by(verification_code=vf).first()
        if lxs400 is None:
            raise ValidationError('Código de verificación no es válido.')

        if User.query.filter_by(lxs400_vc=vf).first():
            raise ValidationError("Alguien ya está usando este código de "
                                  "verificación. Porfavor contacte al "
                                  "administrador.")

    def validate_phone(self, phone):
        phone_n = phone.data
        v_error = ValidationError('Número de teléfono no es '
                                  'válido.')
        if not ((phone_n[0] == '+' or phone_n[0].isdigit()) and
                phone_n[1:].isdigit()):
            raise v_error

        if (phone_n[0] == '+') and (len(phone_n) != 12):
            raise v_error

        if not (phone_n[0] == '+'):
            print(len(phone_n))
            print(phone_n)
            if not (9 <= len(phone_n) <= 11) or (len(phone_n) == 10):
                raise v_error


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Correo electrónico',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar cambio de clave')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField(
        'Repetir contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Guardar')
