"""Plik, w którym znajdują się przekierowania (Route)"""
from flask import render_template, redirect, url_for, flash, request
from flask_babel import _
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Metoda odpowiedzialna za załadowanie klasy logowania i przekazania do wyświetlenia
    :return: render_template
    """
    if current_user.is_authenticated:  # Sprawdza, czy użytkownik jest już zalogowany
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        # Jeśli formularz wysyła GET lub nie powiodła się walidacja, metoda ta zwraca false
        # Pobiera pasujacego usera z bazy (user unikalny) lub zwraca None
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')  # /login?next=/index
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@bp.route('/logout')
def logout():
    """
    Funkcja służąca do wylogowania aktualnego usera.
    :return: przekierowanie do index
    """
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Funkcja odpowiedzialna za przekierowanie na register.html oraz podstawową walidację.
    :return: redirect (index, login lub register)
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    Wyświetla formularz resetu hasła. Sprawdza, czy dany email występuje w bazie
    :return: wyswietla template reset_password_request
    """
    # Jeśli użytkownik jest zalogowany, przekierowuje na stronę główną
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # Wiadomość jest wysyłania niezależnie od tego, czy dany email znajduje się w bazie
        # Ma to na celu zapobiec wycieku informacji, czy rzeczywiście dany klient jest w bazie czy nie
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Wyświetla formularz aktywowany po użyciu linka z tokenem. Służy do zmiany hasła
    :param token: jwt
    :return: wyświetla template reset_password
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
