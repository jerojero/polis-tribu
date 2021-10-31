from flask import render_template, current_app, url_for, redirect
from flask import send_file
from flask_login import current_user, login_required
# from flask_login import current_user, login_required
from .main_email import send_automated_email
from .main_forms import EmailForm, DownloadForm
from app.utils import email_code
from app.main import bp
from config import basedir
import os
import io
import base64

# models
from app.models import User

# utils
from app.utils import save_email_open_times, save_responses
from app.utils import not_completed, not_registered, payment_people

# mail
from random import randint


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html')

# @bp.route('/instructions/')
# def instructions():
#     return render_template('main/instructions.html')


@bp.route('/pixel/<email>/<codigo>')
def pixel(codigo, email):
    # user = request.args.get['codigo']
    gif = 'R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
    gif_str = base64.b64decode(gif)
    save_email_open_times(codigo, email)
    return send_file(io.BytesIO(gif_str), mimetype='image/gif')


@bp.route('/terms_and_conditions/')
def terms_and_conditions():
    return render_template('main/terms_and_conditions.html')


@bp.route('/automated_email/', methods=['GET', 'POST'])
@login_required
def automated_email():
    if str(current_user.id) not in current_app.config['ADMINISTRATORS']:
        return redirect(url_for('main.index'))
    form = EmailForm()
    if form.validate_on_submit():
        file_name = form.csv.data
        email_name = form.body.data
        email_title = form.title.data
        full_file_path = os.path.join(basedir, f'{file_name}.csv')
        current_app.logger.info(full_file_path)
        if os.path.exists(full_file_path):
            everyone = email_code(os.path.join(basedir, f'{file_name}.csv'))
            accumulated_time = 0
            for person in everyone:
                if not User.query.filter_by(lxs400_vc=person[2]).first():
                    time = randint(5, 30)
                    accumulated_time += time
                    send_automated_email(
                        email_name,
                        email_title,
                        person[1],
                        accumulated_time,
                        verification_code=person[2],
                        name=person[0],
                    )
    return render_template('main/automated_email.html', form=form)


@bp.route('/download/', methods=['GET', 'POST'])
@login_required
def download():
    if str(current_user.id) not in current_app.config['ADMINISTRATORS']:
        return redirect(url_for('main.index'))
    form = DownloadForm()
    registered_users = User.query.count(
    ) - len(current_app.config['ADMINISTRATORS'])
    # Because we changed the method for counting we add 30
    completed_d = User.query.filter_by(
        last_question=current_app.config['LASTQ_D']).count()
    completed_x = User.query.filter_by(
        last_question=current_app.config['LASTQ_X']).count() + 30

    if form.validate_on_submit():
        download = form.download.data
        if download == 'email':
            return send_file('../opened_email.csv')
        elif download == 'responsesd':
            save_responses(current_app, doctor=True)
            return send_file('../respuestas_d.csv')
        elif download == 'responsesx':
            save_responses(current_app, doctor=False)
            return send_file('../respuestas_x.csv')
        elif download == 'questions':
            return send_file('../questions.csv')
        elif download == 'notcompleted':
            not_completed(current_app)
            return send_file('../not_completed.csv')
        elif download == 'notreg':
            not_registered(current_app)
            return send_file('../not_registered.csv')
        elif download == 'payment':
            payment_people(current_app)
            return send_file('../payments.csv')

    return render_template('main/download.html',
                           form=form,
                           registered_users=registered_users,
                           completed_d=completed_d,
                           completed_x=completed_x)
