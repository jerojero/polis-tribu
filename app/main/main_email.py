from flask import render_template, current_app
from app.email import send_email


def send_automated_email(email_to_send, email_title, email_address, time, **kwargs):
    send_email(email_title,
               sender=current_app.config['SENDER']
               recipients=[email_address],
               text_body=render_template(
                   f'email/{email_to_send}.txt', **kwargs),
               html_body=render_template(f'email/{email_to_send}.html',
                                         **kwargs),
               schedule=time,)
