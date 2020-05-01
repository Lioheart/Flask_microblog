"""Funkcja pomocnicza wywołująca zadrzenie wysłania emaila na określone adresy"""
from threading import Thread

from flask import current_app
from flask_mail import Message

from app import mail


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
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_async_email(app_async, msg):
    """
    Funkcja ta sprawia, że send_email staje się asynchroniczne
    :param app_async: aplikacja
    :param msg: wiadomość
    """
    with app_async.app_context():
        mail.send(msg)
