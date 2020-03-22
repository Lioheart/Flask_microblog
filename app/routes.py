from flask import render_template

from app import app


@app.route('/')
@app.route('/index')
def index():
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
