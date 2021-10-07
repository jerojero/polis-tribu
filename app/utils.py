import pandas as pd
from app.models import Lxs400
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


def export_codes():
    vfs = []
    emails = []
    names = []
    for user in Lxs400.query.all():
        names.append(user.name)
        emails.append(user.email)
        vfs.append(user.verification_code)
    d = {'nombre:'names, 'email:'emails, 'codigo:'vfs}
    pd.DataFrame(data=d).to_csv(r'codigos.csv', index=False)
