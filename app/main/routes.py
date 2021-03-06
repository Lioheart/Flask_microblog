"""Plik, w którym znajdują się przekierowania (Route)"""
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_babel import _, get_locale
from flask_login import current_user, login_required
from guess_language import guess_language

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, PostForm, SearchForm, MessageForm
from app.models import User, Post, Message, Notification
from app.translate import translate


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    Metoda odpowiedzialna za dane, jakie mają zostać wyświetlone po przekierowaniu na główna stronę
    :return: render_template
    """
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form, posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


# Dynamiczny komponent zawarty w <>
@bp.route('/user/<username>')
@login_required
def user(username):
    """
    Funkcja odpowiedzialna za przekierowanie na stronę o użytkowniku.
    :param username: str
    :return: redirect (user/<username>)
    """
    user_main = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user_main.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user_main.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user_main.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user_main, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.before_app_request
def before_request():
    """
    Funkcja wykonująca się przed załadowanie jakiegokolwiek widoku
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/edit_profile', methods=['GET', 'POST'])
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
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    """
    Dodaje danego użytkownika do obserwowanych dla aktualnie zalogowanego użytkownika
    :param username: user
    :return: przekierowanie do user lub index
    """
    user_follow = User.query.filter_by(username=username).first()
    if user_follow is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user_follow == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user_follow)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """
    Usuwa danego użytkownika z obserwowanych dla aktualnie zalogowanego użytkownika
    :param username: user
    :return: przekierowanie do user lub index
    """
    user_follow = User.query.filter_by(username=username).first()
    if user_follow is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user_follow == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user_follow)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/explore')
@login_required
def explore():
    """
    Wyświetla posty WSZYSTKICH użytkowników.
    :return: wyświetla template index.html
    """
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    """
    Wysyła zapytanie do API w celu tłumaczenia tekstu
    :return: plik JSON z przetłumaczonym tekstem
    """
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_lang'],
                                      request.form['dest_lang'])})


@bp.route('/search')
@login_required
def search():
    """
    Wyszukuje odpowiedniej frazy w postach użytkowników
    :return: przekierowanie do template search.html
    """
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) if total > page * current_app.config[
        'POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    """
    Zwraca dymek z informacjami o użytkowniku
    :param username: użytkownik
    :return: przekierowanie do template user_popup.html
    """
    user_pop = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user_pop)


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    """
    Wysyła wiadomość do okreslonego użytkownika i zapisuje w bazie danych
    :param recipient: użytkownik docelowy
    :return: przekierowanie na stronę z formularzem
    """
    user_msg = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user_msg, body=form.message.data)
        user_msg.add_notification('unread_message_count', user_msg.new_messages())
        db.session.add(msg)
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=_('Send Message'), form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    """
    Zwraca listę wiadomości do danego użytkownika
    :return: przekierowanie na stronę z wiadomościami
    """
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    message = current_user.messages_received.order_by(Message.timestamp.desc()).paginate(page, current_app.config[
        'POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=message.next_num) if message.has_next else None
    prev_url = url_for('main.messages', page=message.prev_num) if message.has_prev else None
    return render_template('messages.html', messages=message.items, next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    """
    Zwraca ilość powiadomień
    :return: JSON
    """
    since = request.args.get('since', 0.0, type=float)
    notification = current_user.notifications.filter(Notification.timestamp > since).order_by(
        Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notification])
