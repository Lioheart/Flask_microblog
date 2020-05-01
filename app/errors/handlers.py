"""Plik odpowiedzialny za wyłapywanie błędów"""
from flask import render_template

from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(err):
    """
    Funkcja odpowiedzialna za przekierowanie na odpowiednią stronę, gdy wystąpi błąd 404.
    :param err:
    :return: strona html
    """
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(err):
    """
    Funkcja odpowiedzialna za przekierowanie na odpowiednią stronę, gdy wystąpi błąd 500
    :param err:
    :return: strona html
    """
    db.session.rollback()
    return render_template('errors/500.html'), 500
