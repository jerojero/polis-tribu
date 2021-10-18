import pandas as pd
from app.models import Section, Lxs400, Question, Answer, Results
from app import db


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
