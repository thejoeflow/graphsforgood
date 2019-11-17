from flask import render_template, request

from ui import webapp


@webapp.route("/login")
def login_register():
    return render_template("login.html")


@webapp.route('/login', methods=['POST'])
def login_attempt():
    username = request.form.get("username")
    password = request.form.get("password")

    # TODO
    # if users.authenticate(username, password):
    #     configure_user_session(username)
    #     return redirect(url_for("main"))
    # else:
    #     return render_template("home.html", title="Welcome to Easy Text Recognition",
    #                            error_msg="You have entered an incorrect password or username")


@webapp.route('/register', methods=['POST'])
def register_new_user():
    username = request.form.get("username")
    password = request.form.get("password")

    # TODO
    # if users.get_user(username) is not None:
    #     print("Failed to register - username is already taken!")
    #     return render_template("home.html", title="Welcome to Easy Text Recognition",
    #                            error_msg="Selected username is already taken. Please choose a different username")
    #
    # if validator.registration(username, password) and users.create_new_user(username, password):
    #     configure_user_session(username)
    #     return redirect(url_for("main"))
    #                     # , error_msg="Registration Successful!")
    #     # return render_template("registration_success.html", title="Registration Successful!")
    # else:
    #     return render_template("home.html", title="Welcome to Easy Text Recognition",
    #                            error_msg="Registration could not be completed at this time. Please try again later")

