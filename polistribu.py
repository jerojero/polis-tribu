from app import create_app, db
from app.models import User, Lxs400, Question, Answer, Section, Results


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'User': User,
            'Lxs400': Lxs400,
            'Question': Question,
            'Answer': Answer,
            'Section': Section,
            'Results': Results}
