import pandas as pd
import numpy as np
from app.models import Section, Lxs400, Question, Answer, Results, User
from app.models import Payment
from app import db
from datetime import datetime


def generate_codes():
    for user in Lxs400.query.all():
        user.set_verification_code()
    db.session.commit()


def load_users(csv):
    df = pd.read_csv(csv)
    for row in df.iloc:
        u = Lxs400(name=row['nombre'],
                   email=row['email'],
                   verification_code=row['codigo'])
        db.session.add(u)
    db.session.commit()


def load_questions(csv):
    df = pd.read_csv(csv)
    for row in df.iloc:
        tail = bool(row['last'])
        if not Section.query.get(int(row['section'])):
            create_section(tail)
        q = Question(
            id=int(row['id']),
            question_type=str(row['q_type']),
            section_id=int(row['section']),
            title=str(row['title']),
            description=str(row['description']),
            optional=bool(row['optional']),
            tail=tail
        )
        print(f"""Question ID: {row['id']}
                  Section ID: {row['section']}
               """)
        db.session.add(q)
    db.session.commit()


def not_completed(current_app, doctor=False):
    user_ids = []
    last_q = current_app.config['LASTQ_D'] if doctor \
        else current_app.config['LASTQ_X']
    len_code = 7 if doctor else 6
    for user in User.query.all():
        if len(user.lxs400_vc) == len_code:
            user_ids.append(user.id)
    user_ids = user_ids[3:] if not doctor else user_ids

    names = []
    users = []
    codes = []
    emails_user = []
    emails_lxs = []

    for uid in user_ids:
        if not Results.query.filter_by(user_id=uid,
                                       question_id=last_q).first():
            u = User.query.get(uid)
            names.append(f"{u.name} {u.last_name}")
            users.append(u.username)
            c = u.lxs400_vc
            codes.append(c)
            emails_user.append(u.email)
            if not doctor:
                emails_lxs.append(Lxs400.query.filter_by(
                    verification_code=c).first().email)

    df = pd.DataFrame(columns=['nombre', 'codigo',
                               'email de registro', 'email base lxs400'])
    df['nombre'] = names
    df['usuario'] = users
    df['codigo'] = codes
    df['email de registro'] = emails_user
    df['email base lxs400'] = emails_lxs

    df.to_csv('not_completed.csv')


def not_registered(current_app, doctor=False):
    data = email_code('codigos.csv')  # TODO: make better, don't be lazy
    df = pd.DataFrame(columns=["nombre", "email", "codigo"])
    nombres = []
    emails = []
    codigos = []
    for row in data:
        codigo = row[2]
        if not User.query.filter_by(lxs400_vc=codigo).first():
            nombres.append(row[0])
            emails.append(row[1])
            codigos.append(row[2])

    df['nombre'] = nombres
    df['email'] = emails
    df['codigo'] = codigos

    df.to_csv('not_registered.csv')


def payment_people(current_app):
    payments = {}
    for user in Payment.query.all():
        if str(user.user_id) not in current_app.config['ADMINISTRATORS']:
            uid = user.user_id
            u = User.query.get(uid).lxs400_vc
            x = Lxs400.query.filter_by(verification_code=u).first()
            payments[uid] = {
                'id de usuario': uid,
                'email lxs400': x.email,
                'nombre lxs400': x.name,
                'nombre': user.first_name,
                'apellido': user.last_name,
                'rut': user.rut,
                'banco': user.bank,
                'tipo de cuenta': user.account,
                'numero de cuenta': user.account_number,
                'permiso': user.permission
            }

    df = pd.DataFrame.from_dict(payments, orient='index',
                                columns=['id de usuario', 'email lxs400',
                                         'nombre lxs400',
                                         'nombre', 'apellido', 'rut',
                                         'banco', 'tipo de cuenta',
                                         'numero de cuenta', 'permiso'])

    df.to_csv('payments.csv')


def save_responses(current_app, doctor=False):
    if doctor:
        filename = 'respuestas_d.csv'
    else:
        filename = 'respuestas_x.csv'

    users = [user_id[0] for user_id in
             db.session.query(Results.user_id).distinct().all()
             if (str(user_id[0]) not in current_app.config['ADMINISTRATORS'])
             and (User.query.get(int(user_id[0])).doctor == doctor)]
    questions = [question_id[0] for question_id in db.session.query(
        Results.question_id).distinct().all()]
    if doctor:
        df = pd.DataFrame(index=users, columns=[
                          'codigo', 'nombre'] + questions)
    else:
        df = pd.DataFrame(index=users, columns=[
                          'codigo', 'nombre', 'folio'] + questions)
    df.index.rename(name='user_id')

    for answer in Results.query.all():
        user = answer.user_id
        if user in users:
            question = answer.question_id
            df.loc[user, question] = answer.answer_text

    codigos = []
    nombres = []
    for user in df.index:
        codigos.append(User.query.get(user).lxs400_vc)
        nombres.append(User.query.get(
            user).name + " " + User.query.get(user).last_name)
    df['nombre'] = nombres
    df['codigo'] = codigos

    df.to_csv(filename)


def get_current_time() -> str:
    return datetime.utcnow().strftime('%d-%m-%YT%H:%M:%S')


def save_email_open_times(codigo: str, email: str) -> None:
    df = pd.read_csv('opened_email.csv', index_col=0)
    try:
        df.at[codigo, email] = get_current_time()
    except Exception:
        df[email] = ''
        df.at[codigo, email] = get_current_time()
    df.to_csv('opened_email.csv')


def save_everyone_who_hasnt_answered() -> None:
    df = pd.read_csv('lxsdata.csv').dropna(subset=['encuesta'])
    df2 = pd.read_csv('codigos.csv')
    codigos = []
    for user in User.query.all():
        codigos.append(user.lxs400_vc)
    codigos = codigos[3:]
    nombres = df[df['Correo'].isin(
        df2[~df2['codigo'].isin(codigos)]['email'])]['nombre']
    emails = df[df['Correo'].isin(
        df2[~df2['codigo'].isin(codigos)]['email'])]['Correo']
    p_numbers = df[df['Correo'].isin(
        df2[~df2['codigo'].isin(codigos)]['email'])]['Telefono']
    codigos_noreg = df2[df2['email'].isin(list(emails))]['codigo']
    df3 = pd.DataFrame(columns=['nombres', 'codigos', 'emails', 'p_numbers'])
    df3['nombres'] = list(nombres)
    df3['codigos'] = list(codigos_noreg)
    df3['emails'] = list(emails)
    df3['p_numbers'] = list(p_numbers)
    df3.to_csv('not_registered.csv')


def load_answers(csv):
    df = pd.read_csv(csv)
    for row in df.iloc:
        a = Answer(
            text=row['text'],
            next_question=int(row['special']),
            question_id=int(row['question'])
        )
        db.session.add(a)
    db.session.commit()


def load_all(question_csv="questions.csv", answers_csv="answers.csv"):
    load_questions(question_csv)
    load_answers(answers_csv)


def delete_response(question_type):
    qs = Question.query.filter_by(question_type=question_type).all()
    rs = [Results.query.filter_by(question_id=question.id).first(
    ) for question in qs if Results.query.filter_by(
        question_id=question.id).first() is not None]
    for response in rs:
        db.session.delete(response)
    db.session.commit()


def delete_all():
    for r in Results.query.all():
        db.session.delete(r)

    for s in Section.query.all():
        db.session.delete(s)

    for q in Question.query.all():
        db.session.delete(q)

    for a in Answer.query.all():
        db.session.delete(a)

    db.session.commit()


def capitalize_first(name):
    capitalized_name = ' '.join([word.lower().capitalize()
                                 for word in name.split(' ')])
    return capitalized_name


def email_code(csv):
    df = pd.read_csv(csv)
    emails = []
    for row in df.iloc:
        emails.append(
            (capitalize_first(row['nombre']),
             row['email'],
             row['codigo'])
        )
    return emails


def export_codes():
    vfs = []
    emails = []
    names = []
    for user in Lxs400.query.all():
        names.append(user.name)
        emails.append(user.email)
        vfs.append(user.verification_code)
    d = {'nombre': names, 'email': emails, 'codigo': vfs}
    pd.DataFrame(data=d).to_csv(r'codigos.csv', index=False)


def create_section(tail=False):
    s = Section(tail=tail)
    db.session.add(s)
    db.session.commit()


def export_questions():
    question_id = []
    question_type = []
    question_text = []
    for question in Question.query.all():
        if question.question_type not in ['fp', 'hd', 'fc']:
            question_id.append(question.id)
            question_type.append(question.question_type)
            question_text.append(question.question_text)

    df = pd.DataFrame(index=question_id, columns=['tipo', 'texto'])
    df.index.rename(name='question_id')

    df.to_csv('questions_export.csv')


def create_question(
        title,
        question_type,
        description=None,
        section_id=None,
        optional=True):
    if section_id:
        section = int(section_id)
    else:
        section = None
    q = Question(title=title,
                 question_type=question_type,
                 description=description,
                 section_id=section,
                 optional=optional)
    db.session.add(q)
    db.session.commit()


def create_answer(text, question_id, next_question=None):
    a = Answer(text=text,
               question_id=question_id,
               next_question=next_question)
    db.session.add(a)
    db.session.commit()


def export_answers():
    results = {'usuarios': [
        f"{user.name} {user.last_name}"
        for user in User.query.all()]}

    for question in Question.query.all():
        if question.question_type not in ['hd', 'fp', 'fc']:
            results[question.id] = []
