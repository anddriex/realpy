# imports
import os

from flask import (Flask, request, session, g, redirect, url_for,
                   abort, render_template, flash, jsonify)
from flask_sqlalchemy import SQLAlchemy

# get the folder where this file runs
basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'my_precious'
USERNAME = 'admin'
PASSWORD = 'admin'

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
            error = 'Nombre de usuario invalida'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Password invalido'
        else:
            session['logged_in'] = True
            flash('Has iniciado sesión')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """User logout/authentication/session management"""
    session.pop('logged_in', None)
    flash('Sesión cerrada exitosamente')
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_entry():
    """Add new post to database."""
    if not session.get('logged_in'):
        abort(401)
    new_entry = models.Flaskr(request.form['title'], request.form['text'])
    db.session.add(new_entry)
    db.session.commit()
    flash('Nueva entrada posteada!')
    return redirect(url_for('index'))


@app.route('/delete/<int:post_id>', methods=['GET'])
def delete_entry(post_id):
    """Delete a post from database"""
    try:
        new_id = post_id
        db.session.query(models.Flaskr).filter_by(post_id=new_id).delete()
        db.session.commit()
        flash('La entrada fue eliminada')
    except Exception as e:
        flash('ERROR: ', e)

    return redirect(url_for('index'))


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_entry(post_id):
    """Edit a post from the database"""
    update_post = db.session.query(models.Flaskr).get({'post_id': post_id})
    if request.method == 'POST':
        try:
            if not session.get('logged_in'):
                abort(401)
            db.session.query(models.Flaskr) \
                .filter_by(post_id=post_id).update({'title': request.form['title'],
                                                    'text': request.form['text']})
            db.session.commit()
            flash('Entrada actualizada!')
        except Exception as e:
            flash(e)

        return redirect(url_for('index'))
    if session.get('logged_in'):
        flash('Editar post')
    else:
        flash('Inicia sesión para editar')
    return render_template('edit.html', update_post=update_post)


if __name__ == '__main__':
    app.run()
