import io
import os
from random import randint
from enum import Enum
from flask import render_template, send_file, url_for
from PIL import Image
from ui import webapp


@webapp.route("/new_graph")
def new_graph():
    return render_template("graph_register.html")


@webapp.route("/graph/<id>")
def graph_details(id):
    return render_template("graph_register.html")


@webapp.route("/graph_img/<id>")
def graph_img(id):
    # TODO: Change this to retrieve graph data from S3 and dynamically generate graph

    img = Image.open(os.path.join(webapp.root_path, 'static/fake_graph{}.png'.format(randint(1, 3))))

    img_obj = io.BytesIO()
    # write PNG in file-object
    img.save(img_obj, 'PNG')
    # move to beginning of file so `send_file()` it will read from start
    img_obj.seek(0)

    return send_file(img_obj, mimetype='image/PNG')


def get_graphs_for_user(user_id):
    # TODO: Get user graphs from database
    graphs = [Graph("abc123", "Monthly Spending", GraphType.PIE, ["test@email.com"], "every day"),
              Graph("abcd1233", "Favourite Fruits", GraphType.LINE_CHART, ["test@email.com", "admin@systen.com"], "every month"),
              Graph("jkdfsb3783", "Network Bandwidth - December", GraphType.BAR_CHART, ["user@domain.ca"], "On Data Change")]
    return graphs


class Graph:

    def __init__(self, id, name, type, subscribers, schedule):
        """
        Instantiates a new graph object
        :param id:
        :param type:
        :param subscribers:
        :param schedule:
        """
        self.id = id
        self.name = name
        self.type = type
        self.subscribers = subscribers
        self.schedule = schedule

    def get_emails(self):
        return ",".join(self.subscribers)


class GraphType(Enum):
    PIE = 1
    LINE_CHART = 2
    BAR_CHART = 3
