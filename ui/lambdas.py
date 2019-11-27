import json
import boto3
from botocore.exceptions import ClientError

from ui import config

# Not the same type of lambda lol
isOk = lambda code: 200 <= code < 300


def generate_graph(type, title, csv_name, username,
                   pie_labels=None,  # pie graph parameter
                   line_xcol=None, line_ycol=None, line_xlabel=None,
                   line_ylabel=None, line_xconstr=None,  # line
                   bar_columns=None, bar_xlabel=None, bar_ylabel=None):  # bar
    graph_args = {
            'type': type,
            'title': title,
            's3_filename': csv_name,
            'username': username
            }

    if type == 'pie':
        if pie_labels is not None:  # optional
            graph_args['labels'] = pie_labels

    elif type == 'line':
        graph_args['x_column'] = line_xcol
        graph_args['y_column'] = line_ycol
        if line_xlabel is not None:  # optional
            graph_args['xlabel'] = line_xlabel
        if line_ylabel is not None:  # optional
            graph_args['ylabel'] = line_ylabel
        if line_xconstr is not None:  # optional
            graph_args['x_constraint'] = line_xconstr

    elif type == 'bar':
        graph_args['columns'] = bar_columns
        if bar_xlabel is not None:
            graph_args['xlabel'] = bar_xlabel
        if bar_ylabel is not None:
            graph_args['ylabel'] = bar_ylabel

    result, resp = call_lambda_function(
            config.lambda_function_names['generate_graph'], **graph_args)

    if result:
        # access s3
        s3 = boto3.resource('s3')
        bucket_name = list(s3.buckets.all())[0].name

        # parse response from lambda function
        filename = resp['Payload'].read().decode("utf-8")
        if filename == 'ERROR':
            return None

        # get a presigned link to graph on s3
        s3_client = boto3.client('s3')
        try:
            graph_link = s3_client.generate_presigned_url(
                    'get_object', Params={'Bucket': bucket_name,
                                          'Key': filename},
                    ExpiresIn=3600)  # link expires in an hour

        except ClientError as e:
           print('ERROR - {}'.format(e))
           return None

    return graph_link


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
    return None if resp.get('Item') is None else User(resp['Item'])


class User:

    def __init__(self, json_file):
        self.email = json_file.get('email')
        self.first_name = json_file.get('First Name')
        self.last_name = json_file.get('Last Name')
        self.password_hash = json_file.get('password_hash')
        self.salt = json_file.get('salt')


# def register_new_graph():
#     {'name': string,
#      'user_email': string,
#     's3_data_file': string,
#      'type': string,
#      'async': boolean,
#      'cron_sched': string,
#      'graph_config': {
#          'title': string,
#          'xlabel': string,
#          'ylabel': string,
#          'x_axis_col': int,
#          'y_axis_col': int[],
#          'labels': string[],
#         }
#      }
#     return True


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
