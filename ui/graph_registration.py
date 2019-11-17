from flask import render_template

from ui import webapp


@webapp.route("/new_graph")
def graph():
    return render_template("graph_register.html")