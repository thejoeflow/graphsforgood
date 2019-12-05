import json
import boto3

from data_objects import User
from ui import config, graph

# Not the same type of lambda lol
isOk = lambda code: 200 <= code < 300


def generate_graph(graph_config, s3_datafile, username, get_external_link = False):

    type = graph_config.graph_type
    graph_args = {
        'type': type,
        'title': graph_config.title ,
        's3_filename': s3_datafile,
        'username': username
    }

    if type == 'pie':
        if not graph_config.customLabels:  # optional
            graph_args['labels'] = graph_config.customLabels

    elif type == 'line':
        graph_args['x_column'] = graph_config.xAxisCol
        # Don't think we're gunna support this for the demo
        graph_args['y_column'] = graph_config.yCols
        if not_empty(graph_config.xLabel):  # optional
            graph_args['xlabel'] = graph_config.xLabel
        if not_empty(graph_config.yLabel):  # optional
            graph_args['ylabel'] = graph_config.yLabel

    elif type == 'bar':
        graph_args['columns'] = graph_config.yCols
        if not_empty(graph_config.xLabel):  # optional
            graph_args['xlabel'] = graph_config.xLabel
        if not_empty(graph_config.yLabel):  # optional
            graph_args['ylabel'] = graph_config.yLabel

    result, resp = call_lambda_function(
        config.lambda_function_names['generate_graph'], **graph_args)

    if result:
        # parse response from lambda function
        filename = resp.strip("\"")
        if filename == 'ERROR':
            return None

        if get_external_link:
            return graph.get_public_url(filename)
        else:
            return filename


def not_empty(s):
    return s and s.strip()


def save_user(email, firstname, lastname, password_hash, salt):
    user = {
        "email_add": email,
        "first_name": firstname,
        "last_name": lastname,
        "password_hash": password_hash,
        "salt": salt
    }
    result, resp = call_lambda_function(config.lambda_function_names['create_user'], **user)
    return result


def get_user(email):
    user = {
        "email_add": email
    }
    result, resp = call_lambda_function(config.lambda_function_names['get_user'], **user)
    if resp is None:
        return None
    else:
        json_str = resp
        resp_json = json.loads(json_str)
        if resp_json['statusCode'] == 200:
            return User(resp_json["body"])
        else:
            return None


def edit_existing_graph():
    return True


def schedule_new_email():
    return True

def register_new_graph(data):
    result, resp = call_lambda_function(config.lambda_function_names['register_new_graph'], **data)
    return resp.strip("\"") if result else None  # graph ID

def get_graph_attribute(username, graphID, attribute):
    event = {
        "email_add": username,
        "graph_id": graphID,
        "attribute": attribute
    }
    result, resp = call_lambda_function(config.lambda_function_names['get_registered_graph'], **event)
    return resp.strip("\"") if result else None

def call_lambda_function(name, async_call=False, **kwargs):
    invocation = 'Event' if async_call else 'RequestResponse'
    payload_json = json.dumps(kwargs)
    resp = boto3.client('lambda').invoke(FunctionName=name, InvocationType=invocation, Payload=str.encode(payload_json))

    if not isOk(resp['StatusCode']):
        print("Lambda Function: {} invocation failed, response: {}".format(name, resp))
        result = False
    else:
        print("Lambda Function: {} invoked successfully".format(name))
        result = True
    return result, resp['Payload'].read().decode("utf-8")
