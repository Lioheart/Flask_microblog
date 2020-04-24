"""Funkcja pomocnicza wywołująca zadrzenie wysłania emaila na określone adresy"""
from threading import Thread

from flask import render_template
from flask_mail import Message

from app import mail, app


def send_email(subject, sender, recipients, text_body, html_body):
    """
    Służy do wysyłania emaili
    :param subject: temat str
    :param sender: email str
    :param recipients: załączniki str
    :param text_body: tekst str
    :param html_body: tekst html str
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_async_email(app_async, msg):
    """
    Funkcja ta sprawia, że send_email staje się asynchroniczne
    :param app_async: aplikacja
    :param msg: wiadomość
    """
    with app_async.app_context():
        mail.send(msg)


def send_password_reset_email(user):
    """
    Wysyła email z linkiem aktywującym reset hasłą dla danego użytkownika
    :param user: Użytkownik z bazy
    """
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token)
               )
