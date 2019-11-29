import json
import boto3
from botocore.exceptions import ClientError

from ui import config

# Not the same type of lambda lol
isOk = lambda code: 200 <= code < 300


def generate_graph(graph_config, s3_datafile, username):

    type = graph_config.graph_type
    graph_args = {
        'type': type,
        'title': graph_config.title ,
        's3_filename': s3_datafile,
        'username': username
    }

    if type == 'pie':
        if not_empty(graph_config.customLabels):  # optional
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
        # access s3
        s3 = boto3.resource('s3')
        bucket_name = list(s3.buckets.all())[0].name

        # parse response from lambda function
        filename = resp['Payload'].read().decode("utf-8").strip("\"")
        if filename == 'ERROR':
            return None

        # get a presigned link to graph on s3
        s3_client = boto3.client('s3', region_name="us-east-1")
        try:
            graph_link = s3_client.generate_presigned_url(
                'get_object', Params={'Bucket': bucket_name,
                                      'Key': filename},
                ExpiresIn=3600)  # link expires in an hour

        except ClientError as e:
            print('ERROR - {}'.format(e))
            return None

    return graph_link


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
    if resp.get('Payload') is None:
        return None
    else:
        json_str = resp['Payload'].read().decode("utf-8")
        resp_json = json.loads(json_str)
        if resp_json['statusCode'] == 200:
            return User(resp_json["body"])
        else:
            return None


class User:

    def __init__(self, json_file):
        self.email = json_file.get('email')
        self.first_name = json_file.get('First Name')
        self.last_name = json_file.get('Last Name')
        self.password_hash = json_file.get('password_hash')
        self.salt = json_file.get('salt')


def edit_existing_graph():
    return True


def schedule_new_email():
    return True


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
    return result, resp
