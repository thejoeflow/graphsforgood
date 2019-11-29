import boto3
import sys
import datetime
import ast
import json


sys.path.insert(1, '../database')
import login_backend


def create_cloudwatch_rule(input_json):
    rule_name = ast.literal_eval(input_json)['rule_name']
    scheduleExpression = ast.literal_eval(input_json)['scheduleExpression']
    client = boto3.client('events', region_name='us-east-1')
    lambda_arn = 'arn:aws:lambda:us-east-1:868512170571:function:send-email'
    scheduleExpressionCRON = "cron({})".format(scheduleExpression)
    client.put_rule(Name=rule_name, ScheduleExpression=scheduleExpressionCRON, State='ENABLED')
    print("Rule Created")


def add_target_to_rule(rule_name, lambda_arn, input_json):
    now = datetime.datetime.now()
    now = str(now)
    ID = now[-15:]
    ID = ID.replace(':', '')
    ID = ID.replace('.', '')
    boto3.client('lambda', region_name = 'us-east-1').add_permission(FunctionName=lambda_arn,
                                          StatementId=ID,
                                          Action="lambda:InvokeFunction",
                                          Principal='events.amazonaws.com'
                                          )

    client = boto3.client('events', region_name='us-east-1')
    client.put_targets(Rule=rule_name,
                       Targets=[{'Id': '1', 'Arn': '{}'.format(lambda_arn), 'Input': '{}'.format(input_json)}])
    print("lambda added as target to the rule")


def send_email(input_json):
    input_json = json.dumps(input_json)
    rule_name = ast.literal_eval(input_json)['rule_name']
    lambda_arn = 'arn:aws:lambda:us-east-1:868512170571:function:send-email'
    create_cloudwatch_rule(input_json)
    add_target_to_rule(rule_name, lambda_arn, input_json)





## Input Parameters

email_add = 'user2@gmail.com'
graph_id = 'user2_gmail_com2019_11_27_21_29_55_286841vyhggjg'
cron ="0/1 * 1/1 * ? *"
# cron = login_backend.get_registered_graph(email_add, graph_id, 'cron')
receiver_email = ["armandordorica@gmail.com"]
# receiver_email = login_backend.get_registered_graph(email_add, graph_id, 'receiver_email')
# file_path = login_backend.get_registered_graph(email_add, graph_id, 'out')
# graphname = login_backend.get_registered_graph(email_add, graph_id, 'graph_Name')
body = "<h1>Body HTML for Graphs for good</h1>"
# body = login_backend.get_registered_graph(email_add, graph_id, 'body')
# subject = login_backend.get_registered_graph(email_add, graph_id, 'subject')
subject = 'Hello from Graphs for Good '
default_email = 'armandordorica@gmail.com'

## Testing
input_dictionary = {
    "rule_name": graph_id,
    "scheduleExpression": cron,
    "bucket_name": "lambda-ses-a3",
    "sender": default_email,
    "recipients": receiver_email,
    "subject":  subject,
    "body_html": body
}

# for k, v in input_dictionary.items():
#     print(k, v)


send_email(input_dictionary);

