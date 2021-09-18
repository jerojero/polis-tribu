from flask import render_template
from flask_login import login_required

from app.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html')


@bp.route('/polis/')
@login_required
def polis():
    return render_template('main/polis.html')


@bp.route('/instructions/')
def instructions():
    return render_template('main/instructions.html')
