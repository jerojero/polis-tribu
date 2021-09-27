from flask import render_template
from flask_login import login_required, current_user

from app import db
from app.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html')


@bp.route('/questionaire/')
@login_required
def questionaire():
    has_visited = current_user.has_visited
    if not has_visited:
        current_user.has_visited = 1
        db.session.commit()
    return render_template('main/questionaire.html', has_visited=has_visited)


@bp.route('/instructions/')
def instructions():
    return render_template('main/instructions.html')
