"""Plik, w którym znajdują się przekierowania (Route)"""
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    Metoda odpowiedzialna za dane, jakie mają zostać wyświetlone po przekierowaniu na główna stronę
    :return: render_template
    """
    posts = [
        {
            'author': {'username': 'Jacek'},
            'body': 'Piękny mamy dziś dzień!'
        },
        {
            'author': {'username': 'susan'},
            'body': 'Mój kot to złooo!!!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Metoda odpowiedzialna za załadowanie klasy logowania i przekazania do wyświetlenia
    :return: render_template
    """
    if current_user.is_authenticated:  # Sprawdza, czy użytkownik jest już zalogowany
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # Jeśli formularz wysyła GET lub nie powiodła się walidacja, metoda ta zwraca false
        # Pobiera pasujacego usera z bazy (user unikalny) lub zwraca None
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')  # /login?next=/index
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    """
    Funkcja służąca do wylogowania aktualnego usera.
    :return: przekierowanie do index
    """
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Funkcja odpowiedzialna za przekierowanie na register.html oraz podstawową walidację.
    :return: redirect (index, login lub register)
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registerd user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
