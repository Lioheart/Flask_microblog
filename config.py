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
