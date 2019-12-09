import datetime
import io
import os
from random import randint

import boto3
from botocore.exceptions import ClientError

from flask import render_template, send_file, request, session, redirect, url_for, flash
from PIL import Image

from email_scheduler.create_cloudwatch_rule import send_email
from ui import webapp, lambdas
from ui.validation import validate_graph_count
from ui import data_objects as do


@webapp.route("/new_graph")
def new_graph():
    return render_template("graph_register.html")


@webapp.route("/new_graph", methods=['POST'])
def register_graph():
    form = request.form
    graph_config = do.GraphConfig.generate_from_request(request)

    subscribers = form.getlist('subscribers')
    subscribers.remove('email')  # Remove placeholder email

    async_schedule = form['sendSchedule'] == 'onDataUpdate'
    cron = form['cron']

    subject = form['emailSubject']
    body = form['emailBody']

    username = session['email']

    if not validate_graph_count(username):
        # do something to tell the user that we can't do this?
        flash("Each user can only generate 20 graphs! You may have to delete a few.", 'error')
        return render_template("graph_register.html")

    csv_file = request.files['dataFile']
    s3_tmp_data = upload_to_s3(csv_file, username)
    s3_tmp_graph = lambdas.generate_graph(graph_config, s3_tmp_data, username)

    post_data = {
        "inp": s3_tmp_data,  # (Temporary input file path)
        "out": s3_tmp_graph,  # (Temporary output file path)
        "email_add": username,
        "graph_name": graph_config.graph_title,
        "graph_type": graph_config.graph_type,
        "email_list": subscribers,
        "Async_val": async_schedule,
        "cron_sche": cron,
        "graph_title": graph_config.graph_title,
        "subject": subject,
        "body": body,
        "x_label": graph_config.x_label,
        "y_label": graph_config.y_label,
        "x_col": graph_config.x_col,
        "y_col": graph_config.y_col,
        "labels": graph_config.labels
    }

    graph_id = lambdas.register_new_graph(post_data)
    if len(graph_id) > 64:
        flash("Error registering graph", 'error')
        return redirect(url_for('main'))
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
    return redirect(url_for('main'))


@webapp.route("/generate_graph", methods=['POST'])
def generate_graph_preview():
    form = request.form
    graph_config = do.GraphConfig.generate_from_request(request)

    subscribers = form.getlist('subscribers')
    subscribers.remove('email')  # Remove placeholder email

    username = session['email']
    csv_file = request.files['dataFile']
    s3_path = upload_to_s3(csv_file, username)
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


def get_graphs(email):
    user = lambdas.get_user(email)


def new_file_timestamp():
    date_temp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
    return str(date_temp).replace(' ', '_').replace('/', '_').replace(':', '_').replace('.', '_')


@webapp.route("/graph/<id>")
def graph_details(id):
    return render_template("graph_register.html")


@webapp.route('/delete/<id>')
def delete_graph(id):
    delete_result = lambdas.delete_graph(session['email'], id)
    if delete_result:
        flash("Graph successfully deleted")
    else:
        flash("Unable to delete graph at this time. Please try again later.")

    return redirect(url_for('main'))


@webapp.route("/graph_img/<id>")
def graph_img(id):
    

    img = Image.open(os.path.join(webapp.root_path, 'static/fake_graph{}.png'.format(randint(1, 3))))

    img_obj = io.BytesIO()
    # write PNG in file-object
    img.save(img_obj, 'PNG')
    # move to beginning of file so `send_file()` it will read from start
    img_obj.seek(0)

    return send_file(img_obj, mimetype='image/PNG')


def get_public_url(filename):
    # get a presignboto3ed link to graph on s3
    s3_client = boto3.client('s3', region_name="us-east-1")
    try:
        # access s3
        s3 = boto3.resource('s3')
        bucket_name = list(s3.buckets.all())[0].name
        return s3_client.generate_presigned_url(
            'get_object', Params={'Bucket': bucket_name,
                                  'Key': filename},
            ExpiresIn=3600)  # link expires in an hour

    except ClientError as e:
        print('ERROR - {}'.format(e))
        return None