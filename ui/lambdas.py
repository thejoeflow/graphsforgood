import json
import boto3


from ui import config, graph
from ui.data_objects import User
from ui.data_objects import GraphConfig

# Not the same type of lambda lol
isOk = lambda code: 200 <= code < 300


def generate_graph(graph_config, s3_datafile, username, get_external_link=False):

    type = graph_config.graph_type
    graph_args = {
        'type': graph_config.graph_type,
        'title': graph_config.graph_title,
        's3_filename': s3_datafile,
        'username': username
    }

    if type == 'pie':
        if not graph_config.labels:  # optional
            graph_args['labels'] = graph_config.labels

    elif type == 'line':
        graph_args['x_column'] = graph_config.x_col
        graph_args['y_column'] = graph_config.y_col
        if not_empty(graph_config.x_label):  # optional
            graph_args['xlabel'] = graph_config.x_label
        if not_empty(graph_config.y_label):  # optional
            graph_args['ylabel'] = graph_config.y_label

    elif type == 'bar':
        graph_args['columns'] = graph_config.y_col
        if not_empty(graph_config.x_label):  # optional
            graph_args['xlabel'] = graph_config.x_label
        if not_empty(graph_config.y_label):  # optional
            graph_args['ylabel'] = graph_config.y_label

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
        resp_json = json.loads(resp)
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


def delete_graph(user, id):
    event = {'email_add': user, 'graph_id': id}
    result, resp = call_lambda_function(config.lambda_function_names['delete_graph'], **event)
    return resp.strip("\"") if result else None


def call_lambda_function(name, async_call=False, **kwargs):
    invocation = 'Event' if async_call else 'RequestResponse'
    payload_json = json.dumps(kwargs)
    resp = boto3.client('lambda', region_name="ca-central-1").invoke(FunctionName=name, InvocationType=invocation, Payload=str.encode(payload_json))

    if not isOk(resp['StatusCode']):
        print("Lambda Function: {} invocation failed, response: {}".format(name, resp))
        result = False
    else:
        print("Lambda Function: {} invoked successfully".format(name))
        result = True
    return result, resp['Payload'].read().decode("utf-8")


def update_data(username, graphID, inp, out):
    event = {
        "email_add": username,
        "graph_id": graphID,
        "inp": inp,
        "out": out,
    }
    result, resp = call_lambda_function(config.lambda_function_names['update_data'], **event)
    return resp.strip("\"") if result else None
