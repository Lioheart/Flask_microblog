"""Plik, w którym znajdują się przekierowania (Route)"""
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.email import send_password_reset_email
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, \
    ResetPasswordForm
from app.models import User, Post


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    Metoda odpowiedzialna za dane, jakie mają zostać wyświetlone po przekierowaniu na główna stronę
    :return: render_template
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template("index.html", title='Home Page', form=form, posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


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


# Dynamiczny komponent zawarty w <>
@app.route('/user/<username>')
@login_required
def user(username):
    """
    Funkcja odpowiedzialna za przekierowanie na stronę o użytkowniku.
    :param username: str
    :return: redirect (user/<username>)
    """
    user_main = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user_main.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user_main.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user_main.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user_main, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.before_request
def before_request():
    """
    Funkcja wykonująca się przed załadowanie jakiegokolwiek widoku
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Funkcja odpowiedzialna za edytowanie zmian o użytkowniku
    :return: przekierowanie do formularza adycji danych
    """
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    """
    Dodaje danego użytkownika do obserwowanych dla aktualnie zalogowanego użytkownika
    :param username: user
    :return: przekierowanie do user lub index
    """
    user_follow = User.query.filter_by(username=username).first()
    if user_follow is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user_follow == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user_follow)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """
    Usuwa danego użytkownika z obserwowanych dla aktualnie zalogowanego użytkownika
    :param username: user
    :return: przekierowanie do user lub index
    """
    user_follow = User.query.filter_by(username=username).first()
    if user_follow is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user_follow == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user_follow)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/explore')
@login_required
def explore():
    """
    Wyświetla posty WSZYSTKICH użytkowników.
    :return: wyświetla template index.html
    """
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    Wyświetla formularz resetu hasła. Sprawdza, czy dany email występuje w bazie
    :return: wyswietla template reset_password_request
    """
    # Jeśli użytkownik jest zalogowany, przekierowuje na stronę główną
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).firts()
        if user:
            send_password_reset_email(user)
        # Wiadomość jest wysyłania niezależnie od tego, czy dany email znajduje się w bazie
        # Ma to na celu zapobiec wycieku informacji, czy rzeczywiście dany klient jest w bazie czy nie
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Wyświetla formularz aktywowany po użyciu linka z tokenem. Służy do zmiany hasła
    :param token: jwt
    :return: wyświetla template reset_password
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
