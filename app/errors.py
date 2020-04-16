"""Plik odpowiedzialny za wyłapywanie błędów"""
from flask import render_template

from app import app, db


@app.errorhandler(404)
def not_found_error(err):
    """
    Funkcja odpowiedzialna za przekierowanie na odpowiednią stronę, gdy wystąpi błąd 404.
    :param err:
    :return: strona html
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(err):
    """
    Funkcja odpowiedzialna za przekierowanie na odpowiednią stronę, gdy wystąpi błąd 500
    :param err:
    :return: strona html
    """
    db.session.rollback()
    return render_template('500.html'), 500
