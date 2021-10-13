from flask import render_template
from app.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html')


@bp.route('/instructions/')
def instructions():
    return render_template('main/instructions.html')


@bp.route('/terms_and_conditions/')
def terms_and_conditions():
    return render_template('main/terms_and_conditions.html')
