"""Obiektowy model bazy danych SQLAlchemy"""
from datetime import datetime

from app import db


class User(db.Model):
    """
    Klasa reprezentuje tabele Users w bazie danych. Zawiera takie pola jak:
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
