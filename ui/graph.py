import datetime
import io
import os
from random import randint
from enum import Enum

import boto3

from database import login_backend
from flask import render_template, send_file, url_for, request, session
from PIL import Image

from email_scheduler.create_cloudwatch_rule import send_email
from ui import webapp, lambdas


@webapp.route("/new_graph")
def new_graph():
    return render_template("graph_register.html")


@webapp.route("/new_graph", methods=['POST'])
def register_graph():

    form = request.form
    graph_config = GraphConfig(request)

    subscribers = form.getlist('subscribers')
    subscribers.remove('email')  # Remove placeholder email

    async_schedule = form['sendSchedule'] == 'onDataUpdate'
    cron = form['cron']

    subject = form['emailSubject']
    body = form['emailBody']

    username = session['email']
    s3_tmp_data = upload_to_s3(graph_config.csvFile, username)
    s3_tmp_graph = lambdas.generate_graph(graph_config, s3_tmp_data, username)

    post_data = {
        "inp": s3_tmp_data,  # (Temporary input file path)
        "out": s3_tmp_graph,  # (Temporary output file path)
        "email_add": username,
        "graph_name": graph_config.title,
        "graph_type": graph_config.graph_type,
        "email_list": subscribers,
        "Async_val": async_schedule,
        "cron_sche": cron,
        "graph_title": graph_config.title,
        "subject": subject,
        "body": body,
        "x_label": graph_config.xLabel,
        "y_label": graph_config.yLabel,
        "x_col": graph_config.xAxisCol,
        "y_col": graph_config.yCols,
        "labels": graph_config.customLabels
    }

    graph_id = lambdas.register_new_graph(post_data)
    s3_graph_out = lambdas.get_graph_attribute(username, graph_id, 'out')

    sched_data = {
        "rule_name": graph_id,
        "filename": s3_graph_out,
        "scheduleExpression": cron,
        "bucket_name": "lambda-ses-a3",
        "sender": username,
        "recipients": subscribers,
        "subject": subject,
        "body_html": body
    }

    send_email(sched_data)

    return render_template("graph_register.html")


@webapp.route("/generate_graph", methods=['POST'])
def generate_graph_preview():
    form = request.form
    graph_config = GraphConfig(request)

    subscribers = form.getlist('subscribers')
    subscribers.remove('email')  # Remove placeholder email

    username = session['email']
    s3_path = upload_to_s3(graph_config.csvFile, username)
    graph_img_link = lambdas.generate_graph(graph_config, s3_path, username, get_external_link=True)

    return graph_img_link if graph_img_link is not None else ""


def upload_to_s3(file, user_email):
    bucket = list(boto3.resource('s3').buckets.all())[0]
    filename, ext = file.filename.rsplit('.', 1)
    name = str(user_email).replace('@', '_').replace('.', '_')
    s3_path = 'temp' + "/" + name + "/" + new_file_timestamp() + "." + ext
    resp = bucket.put_object(Key=s3_path, Body=file)
    print("Upload data response: ")
    print(resp)
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

class GraphConfig:

    def __init__(self, request):
        form = request.form
        self.csvFile = request.files['dataFile']

        self.graph_type = form['graphType']
        if self.graph_type == "pie":
            i = 0
        elif self.graph_type == "bar":
            i = 1
        else:  # line chart
            i = 2

        self.title = form.getlist('title')[i]
        self.customLabels = form.getlist('customLabels')[i].split(",")
        xCol = form.get('xAxisCol')
        if not_empty(xCol):
            self.xAxisCol = int(xCol)
        else:
            self.xAxisCol = None

        self.yCols = [int(i) for i in form.getlist('yColumns')]
        if i == 1 or i == 2:
            self.xLabel = form.getlist('xLabel')[i - 1]
            self.yLabel = form.getlist('yLabel')[i - 1]
        else:
            self.xLabel = None
            self.yLabel = None


def not_empty(s):
    return s and s.strip()
