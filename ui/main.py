from flask import request, render_template, session, redirect, url_for

from ui import webapp, graph


# @webapp.before_request
# def check_session():
#     """
#     This hook checks every request made to the application to ensure a non-logged in user is not accessing a resource
#     (html page, file) they are not authorized to access.
#     :return: The login page if the user is trying to access a restricted resource
#     """
#     public_pages = ('/login', '/register', '/logout', '/static', '/api')
#     if not request.path == '/' and not request.path.startswith(public_pages) and 'username' not in session:
#         return render_template("login.html", error_msg="You must log in to access this page")


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