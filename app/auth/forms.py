from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models import User, Lxs400


class MyBaseForm(FlaskForm):
    class Meta:
        locales = ['es_ES', 'es']


class LoginForm(MyBaseForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Inicia sesión')


class RegistrationForm(MyBaseForm, FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    email = StringField('Correo electrónico', validators=[DataRequired(),
                                                          Email()])
    email2 = StringField('Repetir correo electrónico', validators=[
                         DataRequired(), EqualTo('email')])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField(
        'Repetir contraseña', validators=[DataRequired(), EqualTo('password')])
    verification_code = StringField('Codigo de verificación',
                                    validators=[DataRequired()])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Este nombre de usuario ya está registrado.'
                                  ' Porfavor elegir otro'
                                  ' nombre de usuario')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Este correo electrónico ya está siendo '
                                  'utilizado. Por favor use otra dirección de '
                                  'correo electrónico.')

    def validate_verification_code(self, verification_code):
        lxs400 = Lxs400.query.filter_by(
                    verification_code=verification_code.data).first()
        if lxs400 is None:
            raise ValidationError('Código de verificación no es válido.')

        if User.query.filter_by(lxs400_vc=verification_code.data).first():
            raise ValidationError("Alguien ya está usando este código de " 
                                  "verificación. Porfavor contacte al "
                                  "administrador.")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Correo electrónico', 
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar cambio de clave')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField(
        'Repetir contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Guardar')
