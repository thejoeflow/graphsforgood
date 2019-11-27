import boto3
import sys
import datetime
import ast

sys.path.insert(1, '../database')
import login_backend

email_add = 'user4@gmail.com'


# login_backend.get_registered_graph(email_add, 'user4_gmail_com2019_11_27_17_31_18_052000graph1', 'cron')


def create_cloudwatch_rule(input_json):
    rule_name = ast.literal_eval(input_json)['rule_name']
    scheduleExpression = ast.literal_eval(input_json)['scheduleExpression']
    client = boto3.client('events')
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
    boto3.client('lambda').add_permission(FunctionName=lambda_arn,
                                          StatementId=ID,
                                          Action="lambda:InvokeFunction",
                                          Principal='events.amazonaws.com',
                                          )

    client = boto3.client('events')
    client.put_targets(Rule=rule_name,
                       Targets=[{'Id': '1', 'Arn': '{}'.format(lambda_arn), 'Input': '{}'.format(input_json)}])
    print("lambda added as target to the rule")


def send_email(input_json):
    rule_name = ast.literal_eval(input_json)['rule_name']
    lambda_arn = 'arn:aws:lambda:us-east-1:868512170571:function:send-email'
    create_cloudwatch_rule(input_json)
    add_target_to_rule(rule_name, lambda_arn, input_json)


## Testing
input_json = """
{ "rule_name": "Every-minute-10", "scheduleExpression": "0/1 * 1/1 * ? *", "bucket_name" : "lambda-ses-a3","sender" : "armandordorica@gmail.com","recipients" : ["armandordorica@gmail.com", "armando.ordorica@mail.utoronto.ca"], "subject":  "TESTING S3 TO EMAIL FUNCTION from Joes account and passing input parameters to lambda as JSON from Cloudwatch and boto3", "body_html" : "<h1>Testing S3 to email function from Joes account and lambda through Cloudwatch and boto3</h1>" }
"""

send_email(input_json);

# email_add = 'user4@gmail.com'
# cron = login_backend.get_registered_graph(email_add, 'user4_gmail_com2019_11_27_17_31_18_052000graph1', 'cron')
# receiver_email = get_registered_graph(email_add, 'user4_gmail_com2019_11_27_17_31_18_052000graph1', 'receiver_email')
# file_path = get_registered_graph(email_add, 'user4_gmail_com2019_11_27_17_31_18_052000graph1', 'out')
# graphname = get_registered_graph(email_add, 'user4_gmail_com2019_11_27_17_31_18_052000graph1', 'graph_Name')
