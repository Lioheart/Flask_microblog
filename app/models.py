"""Obiektowy model bazy danych SQLAlchemy"""
import json
from datetime import datetime
from hashlib import md5
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
from app.search import add_to_index, remove_from_index, query_index

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


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
    messages_sent - wiadomości wysłane, klucz obcy
    messages_received - wiadomości odebrane, klucz obcy
    last_message_read_time - czas ostatniego odczytania wiadomości
    notifications - powiadomienia
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
    messages_sent = db.relationship(
        'Message',
        foreign_keys='Message.sender_id',
        backref='author', lazy='dynamic'
    )
    messages_received = db.relationship(
        'Message',
        foreign_keys='Message.recipient_id',
        backref='recipient',
        lazy='dynamic'
    )
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

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
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, current_app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')

    def new_messages(self):
        """
        Zwraca ilość nieprzeczytanych wiadomości
        :return: zapytanie query - int
        """
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        """
        Dodaje powiadomienie
        :param name: nazwa str
        :param data: dane str
        :return:
        """
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    @staticmethod
    def verify_reset_password_token(token):
        """
        Metoda sprawdzająca, czy token został poprawnie zweryfikowany
        :param token: jwt
        :return: użytkownik o podanym id
        """
        try:
            id_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return User.query.get(id_token)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(SearchableMixin, db.Model):
    """
    Klasa reprezentująca tabelę Posts w bazie danych. Zawiera:
    id - ID typu int,
    body - ciało, czyli tekst właściwy typu str,
    timestamp - znacznik czasu typu datetime
    user_id - klucz obcy ID tabeli User typu int
    language - język, w którym napisano post typu string
    __searchable__ - pole wyszukiwania
    """
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Message(db.Model):
    """
    Klasa reprezentująca tabelę Message (wiadomości). Zawiera:
    id - ID typu int,
    sender_id - ID użytkownika wysyłającego, klucz obcy,
    recipient_id - ID użytkownika docelowego, klucz obcy,
    body - kolumna z wiadomością typu str
    timestamp - znacznik czasu typu datetime
    """
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Notification(db.Model):
    """
    Klasa opisująca powiadomienia o ilości wiadomości. Zawiera:
    id - ID powiadomień, typu int
    name - nazwa, typu str
    user_id - ID użytkownika, którego dotyczą powiadomienia, klucz obcy
    timestamp - znacznik czasu
    payload_json - plik JSON
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        """
        Zwraca wartość w formie pliku JSON
        :return: JSON
        """
        return json.loads(str(self.payload_json))


@login.user_loader
def load_user(id_user):
    """
    Zwraca obiekt User po zadanym ID
    :param id_user: str
    :return: User
    """
    return User.query.get(int(id_user))


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
