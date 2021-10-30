import pandas as pd
import numpy as np
from app.models import Section, Lxs400, Question, Answer, Results, User
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


def save_responses(current_app, doctor=False):
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

    for question in questions:
        qs = []
        for user in df.index:
            r = Results.query.filter_by(
                question_id=question, user_id=user).first()
            if r:
                qs.append(r.answer_text)
            else:
                qs.append("")
        df[question] = qs

    codigos = []
    nombres = []
    for user in df.index:
        codigos.append(User.query.get(user).lxs400_vc)
        nombres.append(User.query.get(
            user).name + " " + User.query.get(user).last_name)
    df['nombre'] = nombres
    df['codigo'] = codigos

    if doctor:
        filename = 'respuestas_d.csv'
    else:
        filename = 'respuestas_x.csv'
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
