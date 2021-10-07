# Flask stuff
from app import db
from app import login
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Generate Random String
import random
import string

# Password reset
from time import time
import jwt


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    consent = db.Column(db.Boolean)
    rut = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    doctor = db.Column(db.Boolean)
    has_visited = db.Column(db.Boolean)
    lxs400_vc = db.Column(db.String(64),
                          db.ForeignKey('lxs400.verification_code'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return User.query.get(id)

    def __repr__(self):
        return f"<User {self.username}, {self.email}, {self.lxs400_vc}>"


class Lxs400(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120))
    verification_code = db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref='lxs400',
                           uselist=False, cascade="all")

    def set_verification_code(self, attempts=0):
        if self.verification_code:
            return
        verification_code = ''.join([random.choice(
            string.ascii_letters + string.digits) for _ in range(6)])
        if attempts > 10:
            raise AssertionError(
                "We have probably run out of verification codes")

        if Lxs400.query.filter(Lxs400.verification_code == verification_code) \
                .first():
            self.set_verification_code(attempts + 1)

        self.verification_code = verification_code

    def __repr__(self):
        return f"<User ID: {self.id}, Name: {self.name}, " \
               f"VF: {self.verification_code}>"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
