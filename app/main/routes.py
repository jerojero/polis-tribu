from flask import render_template
from flask import current_app
# from flask_login import current_user, login_required
from .main_email import send_automated_email
from .main_forms import EmailForm
from app.utils import email_code
from app.main import bp
from config import basedir
import os


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


@bp.route('/automated_email/', methods=['GET', 'POST'])
# @login_required
def automated_email():
    form = EmailForm()
    if form.validate_on_submit():
        file_name = form.csv.data
        email_name = form.body.data
        email_title = form.title.data
        full_file_path = os.path.join(basedir, f'{file_name}.csv')
        current_app.logger.info(full_file_path)
        if os.path.exists(full_file_path):
            everyone = email_code(os.path.join(basedir, f'{file_name}.csv'))
            for person in everyone:
                send_automated_email(
                    email_name,
                    email_title,
                    person[1],
                    verification_code=person[2],
                    name=person[0]
                )
    return render_template('main/automated_email.html', form=form)
