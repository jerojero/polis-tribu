from flask_mail import Message
from flask import current_app
from app import mail
from time import sleep

# Multi thread support
from threading import Thread


def send_async_email(app, msg, recipients, schedule):
    with app.app_context():
        current_app.logger.info(
            f'About to send email to {recipients}, will wait {schedule} seconds')
        sleep(schedule)
        mail.send(msg)
        current_app.logger.info(f'Sent email to {recipients}')


def send_email(subject, sender, recipients, text_body, html_body, schedule):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg,
                 recipients, schedule)).start()
