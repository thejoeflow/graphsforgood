import random
import string
from datetime import timedelta

from Crypto.Hash import SHA256
from flask import render_template, request, session, redirect, url_for

from ui import webapp, lambdas, validation


@webapp.route("/login")
def login_register():
    return render_template("login.html")


def authenticate(email, password):
    """
    Attempts to authenticate the user with the supplied credentials
    :param email:
    :param password:
    :return: True if user credentials are correct. False if authentication failed.
    """
    try:
        user = lambdas.get_user(email)
        if user is not None:
            password_given = sha256_hash_hex(password, user.salt)
            print("Email:{}, user_email:{} ".format(email, user.email))
            return (email == user.email) & (password_given == user.password_hash)
        else:
            return False
    except Exception as e:
        print("User authentication failed for user: " + email, e, "\n")
        return False


@webapp.route('/login', methods=['POST'])
def login_attempt():
    email = request.form.get("email")
    password = request.form.get("password")
    print("Email:{}, password:{} ".format(email, password))

    if "@" not in email:
        return render_template("login.html", error_msg="An input email must be of the form user_email@domain.com ")
    if "." not in email:
        return render_template("login.html", error_msg="An input email must be of the form user_email@domain.com ")
    if authenticate(email, password):
        configure_user_session(email)
        return redirect(url_for("main"))
    else:
        return render_template("login.html", error_msg="You have entered an incorrect password or email")


@webapp.route('/register', methods=['POST'])
def register_new_user():
    email = request.form.get("email")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    password = request.form.get("password")
    salt = salt_generator()
    password_hash = sha256_hash_hex(password, salt)

    if "@" not in email:
        return render_template("login.html", error_msg="Invalid email format")
    if "." not in email:
        return render_template("login.html", error_msg="Invalid email format")
    if lambdas.get_user(email) is not None:
        print("Failed to register - email is already taken!")
        return render_template("login.html", error_msg="Email is already registered. Please choose a different email")

    if validation.registration(email, password) and \
            lambdas.save_user(email, firstname, lastname, password_hash, salt):
        return render_template("login.html", msg="Registration Successful!")
    else:
        return render_template("login.html",
                               error_msg="Registration could not be completed at this time. Please try again later")


def configure_user_session(email):
    """
    Creates a cookie-based user session for an authenticated user and sets the session timeout to be 24 hours
    :param email:
    """
    session['email'] = email
    session.permanent = True
    webapp.permanent_session_lifetime = timedelta(hours=24)


def sha256_hash_hex(data, salt=""):
    sha = SHA256.new()
    sha.update(data.encode("utf-8"))
    sha.update(salt.encode("utf-8"))
    return sha.hexdigest()


def salt_generator():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(10))
