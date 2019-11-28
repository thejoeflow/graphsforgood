import datetime
import io
import os
from random import randint
from enum import Enum

import boto3

from database import login_backend
from flask import render_template, send_file, url_for, request, session
from PIL import Image
from ui import webapp, lambdas


@webapp.route("/new_graph")
def new_graph():
    return render_template("graph_register.html")


@webapp.route("/new_graph", methods=['POST'])
def register_graph():
    form = request.form
    csvFile = request.files['dataFile']
    graph_type = form['graphType']
    if graph_type == "pie":
        i = 0
    elif graph_type == "bar":
        i = 1
    else:  # line chart
        i = 2

    title = form.getlist('title')[i]
    customLabels = form.getlist('customLabels')[i]
    xAxisCol = form['xAxisCol']
    if i == 1 or i == 2:
        xLabel = form.getlist('xLabel')[i - 1]
        yLabel = form.getlist('yLabel')[i - 1]

    subscribers = form.getlist('subscribers')
    subscribers.remove('email')  # Remove placeholder email

    async = form['sendSchedule'] == 'onDataUpdate'
    cron = form['cron']

    return render_template("graph_register.html")


@webapp.route("/generate_graph", methods=['POST'])
def generate_graph_preview():
    form = request.form
    csvFile = request.files['dataFile']

    graph_type = form['graphType']
    if graph_type == "pie":
        i = 0
    elif graph_type == "bar":
        i = 1
    else:  # line chart
        i = 2

    title = form.getlist('title')[i]
    customLabels = form.getlist('customLabels')[i]
    xAxisCol = form.get('xAxisCol')
    if i == 1 or i == 2:
        xLabel = form.getlist('xLabel')[i - 1]
        yLabel = form.getlist('yLabel')[i - 1]
    else:
        xLabel = None
        yLabel = None

    subscribers = form.getlist('subscribers')
    subscribers.remove('email')  # Remove placeholder email

    async = form['sendSchedule'] == 'onDataUpdate'
    cron = form['cron']

    username = session['email']
    s3_path = upload_to_s3(csvFile, username)
    graph_img_link = lambdas.generate_graph(graph_type, title, s3_path, username,
                                            labels=customLabels, line_xcol=xAxisCol,
                                            xlabel=xLabel, ylabel=yLabel)
    return graph_img_link


def upload_to_s3(file, user_email):
    bucket = list(boto3.resource('s3').buckets.all())[0]
    filename, ext = file.filename.rsplit('.', 1)
    name = str(user_email).replace('@', '_').replace('.', '_')
    s3_path = 'temp' + "/" + name + "/" + new_file_timestamp() + "." + ext
    bucket.put_object(Key=s3_path, Body=file)
    return s3_path


def new_file_timestamp():
    date_temp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
    return str(date_temp).replace(' ', '_').replace('/', '_').replace(':', '_').replace('.', '_')


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
              Graph("abcd1233", "Favourite Fruits", GraphType.LINE_CHART, ["test@email.com", "admin@systen.com"],
                    "every month"),
              Graph("jkdfsb3783", "Network Bandwidth - December", GraphType.BAR_CHART, ["user@domain.ca"],
                    "On Data Change")]
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
