from enum import Enum

import boto3
from flask import render_template, session, redirect, url_for, make_response, jsonify, request
from ui import login

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


@webapp.route('/api/update', methods=['POST'])
def update_data():
    user = request.form.get('email', default='', type=str)
    password = request.form.get('password', default='', type=str)
    gid = request.form.get('gid', default='', type=str)
    file = request.files['file']
    if not login.authenticate(user, password):
        return make_response(jsonify({'result': 'Validation failed - Invalid email/password.'}), 401)

    usr_data = lambdas.get_user(user)
    graph_exists = False
    csv_path = ''

    for g in usr_data.graphs:
        if g.id == gid:
            graph_exists = True
            csv_path = g.inp_s3
            graph_config = g.config
            break

    if not graph_exists:
        return make_response(jsonify({'result': 'Invalid gid.'}), 401)

    bucket = boto3.resource('s3').Bucket('lambda-ses-a3')
    bucket.put_object(Key=csv_path, Body=file)
    resp = {'Upload': 'Good'}

    # generate new graph
    ggen_result = str(lambdas.generate_graph(graph_config, csv_path, usr_data.email))
    if (ggen_result is not None):
        resp['graph gen'] = ggen_result

    return make_response(jsonify(resp), 200)

