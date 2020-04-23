"""Plik konfiguracyjny"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Klasa konfiguracyjna, zawierająca SECRET_KEY
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nigdy-nie-zgadniesz'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['caco7.lioheart@gmail.com', 'zelazek_pawel@wp.pl']
    POSTS_PER_PAGE = 25
