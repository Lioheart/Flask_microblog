"""Plik, w którym znajdują się przekierowania (Route)"""
from flask import render_template, flash, redirect, url_for

from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    """
    Metoda odpowiedzialna za dane, jakie mają zostać wyświetlone po przekierowaniu na główna stronę
    :return: render_template
    """
    user = {'username': 'Michał'}
    posts = [
        {
            'author': {'username': 'Jacek'},
            'body': 'Piękny mamy dziś dzień!'
        },
        {
            'author': {'username': 'Dagmara'},
            'body': 'Mój kot to złooo!!!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Metoda odpowiedzialna za załadowanie klasy logowania i przekazania do wyświetlenia
    :return: render_template
    """
    form = LoginForm()
    if form.validate_on_submit():
        # Jeśli formularz wysyła GET lub nie powiodła się walidacja, metoda ta zwraca false
        flash('Login requested for user {}, remember_me={} !'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
