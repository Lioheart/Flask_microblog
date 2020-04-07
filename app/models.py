"""Obiektowy model bazy danych SQLAlchemy"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class User(UserMixin, db.Model):
    """
    Klasa reprezentuje tabele Users w bazie danych. Dziedziczy po UserMixin (od flask-login) oraz db.Model (za bazę
    danych).
    Zawiera takie pola jak:
    id - ID typu int,
    username - login typu str,
    email - email typu str,
    password_hash - hasło typu str
    posts - posty typu klucz obcy
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        """
        Ustawia hasło i hashuje je
        :param password: str
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Sprawdza poprawność zhashowanego hasła i zwraca True lub False
        :param password: str
        :return: boolean
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    """
    Klasa reprezentująca tabelę Posts w bazie danych. Zawiera:
    id - ID typu int,
    body - ciało, czyli tekst właściwy typu str,
    timestamp - znacznik czasu typu datetime
    user_id - klucz obcy ID tabeli User typu int
    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id_user):
    """
    Zwraca obiekt User po zadanym ID
    :param id_user: str
    :return: User
    """
    return User.query.get(int(id_user))
