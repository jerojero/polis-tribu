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

# Form stuff
from wtforms import RadioField
from wtforms.validators import Optional, DataRequired


class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answers = db.Column(db.Text)
    answer_text = db.Column(db.Text)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<ID: {self.id}, User: {self.user_id}, Question: {self.question_id}, Answer: {self.answers}>\n"


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
    last_question = db.Column(db.Integer)
    lxs400_vc = db.Column(db.String(64),
                          db.ForeignKey('lxs400.verification_code'))
    result = db.relationship('Results', backref='user',
                             uselist=False, cascade="all")

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


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    question_type = db.Column(db.String(64))
    answer_options = db.Column(db.Text)
    head = db.Column(db.Boolean)
    tail = db.Column(db.Boolean)
    previous_question = db.Column(db.Integer)
    next_question = db.Column(db.Integer)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    optional = db.Column(db.Boolean)
    answer = db.relationship("Answer", backref="question", lazy="dynamic")
    result = db.relationship('Results', backref='question',
                             uselist=False, cascade="all")

    def get_next_question(self, answer_id=None):
        if not answer_id:
            return self.next_question
        a = self.answer.filter_by(id=answer_id).first()
        if a:
            return a.next_question
        else:
            return self.next_question

    def set_next_question(self, next_q, answer_id=None):
        if not answer_id:
            self.next_question = next_q
        else:
            Answer.query.get(answer_id).next_question = next_q

    def __repr__(self):
        return f"<ID: {self.id}, type: {self.question_type}, title: {self.title} >\n"


class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    next_question = db.Column(db.Integer)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    def __repr__(self):
        return f"<ID: {self.id} text: {self.text}, question: {self.question_id}>\n"


class Section(db.Model):
    __tablename__ = 'section'
    id = db.Column(db.Integer, primary_key=True)
    tail = db.Column(db.Boolean)
    questions = db.relationship(
        "Question", backref="section", lazy="dynamic")

    def get_previous_section(self):
        took_me_here = Answer.query.filter_by(next_question=self.id).first()
        if not took_me_here:
            return self.id - 1
        return Question.query.get(took_me_here.question_id).section_id


@ login.user_loader
def load_user(id):
    return User.query.get(int(id))
