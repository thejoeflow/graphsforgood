from enum import Enum

from flask import render_template, session, redirect, url_for

from ui import lambdas
from ui import webapp


@webapp.route('/')
def index():
    return redirect(url_for("main")) if 'email' in session else redirect(url_for("login_register"))


@webapp.route('/main')
def main():
    user = lambdas.get_user(session['email'])
    return render_template("main.html", graphs=user.graphs)


@webapp.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))
