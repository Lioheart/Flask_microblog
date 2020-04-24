"""Obiektowy model bazy danych SQLAlchemy"""
from datetime import datetime
from hashlib import md5
from time import time

import jwt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login, app

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


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
    about_me - o mnie typu str
    last_seen - czas ostatniej wizyty typu datetime
    followed - relacja tabeli followers typu db.Table, klucz obcy
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

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

    def avatar(self, size):
        """
        Zwraca gravatar automatyczny na podstawie adresu email
        :param size: rozmiar awatara
        :return: link do awatara w formie .jpg
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=robohash&s={}'.format(digest, size)

    def follow(self, user):
        """
        Służy do zaznaczenia którego użytkownika mamy obserwować
        :param user: użytkownik, którego będziemy obserwować
        """
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """
        Służy do zaznaczenia którego użytkownika mamy przestać obserwować
        :param user: użytkownik, którego przestaniemy obserwować
        """
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """
        Sprawdza, czy obserwujemy danego użytkownika
        :param user:
        :return: zwraca wartość boolean
        """
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """
        Wyświetla wszystkie posty nasze i użytkowników, które śledzimy
        :return: Zwraca zapytanie odnośnie postów użytkowników, których śledzimy i naszych, posortowanych według daty
        """
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        """
        Metoda generująca token służący do resetowania hasła
        :param expires_in: czas życia tokena int
        :return: token jwt
        """
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        """
        Metoda sprawdzająca, czy token został poprawnie zweryfikowany
        :param token: jwt
        :return: użytkownik o podanym id
        """
        try:
            id_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return User.query.get(id_token)

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
