# imports
import os
from dotenv import load_dotenv
from random import randint
from flask import (Flask, request, session, g, redirect, url_for,
                   abort, render_template, flash, jsonify)
from flask_sqlalchemy import SQLAlchemy
from email_service import send_verification_email

load_dotenv()
# get the folder where this file runs
basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'my_precious'
USERNAME = 'andres@tinkin.one'
PASSWORD = 'hola'
VERIFICATION_CODE = '1234'
# define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# database config
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = False

# create and initialize app
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

import models


def build_code():
    return ''.join([str(randint(0, 9)) for i in range(4)])


@app.route('/')
def index():
    """Searches the database for entries, then displays them."""
    entries = db.session.query(models.Flaskr)
    return render_template('index.html', entries=entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            code = app.config['VERIFICATION_CODE'] if app.config['TESTING'] else build_code()
            send_verification_email(app.config['USERNAME'], code)
            session['verification_code'] = code
            flash('Te hemos enviado el código de verificación a tu correo')
            return redirect(url_for('verify'))

    return render_template('login.html', error=error)


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """User verify account with code sent via email"""
    error = None
    if request.method == 'POST':
        if request.form['verification_code'] != session.get('verification_code'):
            error = 'Incorrect verification code entered'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('verify.html', error=error)


@app.route('/logout')
def logout():
    """User logout/authentication/session management"""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_entry():
    """Add new post to database."""
    if not session.get('logged_in'):
        abort(401)
    new_entry = models.Flaskr(request.form['title'], request.form['text'])
    db.session.add(new_entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))


@app.route('/delete/<int:post_id>', methods=['GET'])
def delete_entry(post_id):
    """Delete a post from database"""
    result = {'status': 0, 'message': 'Error'}
    try:
        new_id = post_id
        db.session.query(models.Flaskr).filter_by(post_id=new_id).delete()
        db.session.commit()
        result = {'status': 1, 'message': "Post Deleted"}
        flash('The entry was deleted.')
    except Exception as e:
        result = {'status': 0, 'message': repr(e)}

    return jsonify(result)


@app.route('/edit', methods=['PUT'])
def edit_entry(message_id):
    """Edit a post from the database"""
    pass


if __name__ == '__main__':
    app.run()
