import json
import boto3
from ui import config

# Not the same type of lambda lol
isOk = lambda code: 200 <= code < 300


def generate_graph():
    graph_img = None
    return graph_img


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
