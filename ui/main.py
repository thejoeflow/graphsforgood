from flask import request, render_template, session, redirect, url_for

from ui import webapp, graph

@webapp.route('/')
def index():
    return redirect(url_for("main")) if 'username' in session else redirect(url_for("login_register"))


@webapp.route('/main')
def main():
    user_id = 123456
    graphs = graph.get_graphs_for_user(user_id)
    return render_template("/main.html", graphs=graphs)


@webapp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))