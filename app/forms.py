"""Plik z klasami zawierający wszelkie niezbędne formularze www"""
from flask_babel import lazy_gettext as _l, _
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length

from app.models import User


class LoginForm(FlaskForm):
    """Klasa odpowiedzialna za formularz logowania"""
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    """Klasa odpowiedzialna za formularz rejestracji użytkownika"""
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        """
        Metoda sprawdzająca, czy dany użytkownik występuje już w bazie danych.
        :param username: str
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        """
        Metoda sprawdzająca, czy dany email występuje już w bazie danych.
        :param email: str
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))


class EditProfileForm(FlaskForm):
    """Klasa odpowiedzialna za formularz edycji danych użytkownika"""
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """
        Metoda sprawdzająca, czy dany użytkownik nie występuje już w bazie
        :param username: str
        """
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    """Klasa opisuje formularz postów użytkownika"""
    post = TextAreaField(_l('Say something new'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))


class ResetPasswordRequestForm(FlaskForm):
    """Klasa opisuje formularz resetowania hasła"""
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    """Klasa reprezentująca pola służące do resetowania hasłą"""
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))
