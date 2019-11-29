import boto3
import sys
import datetime
import ast
import json

def create_cloudwatch_rule(input_json):
    rule_name = ast.literal_eval(input_json)['rule_name']
    scheduleExpression = ast.literal_eval(input_json)['scheduleExpression']
    client = boto3.client('events', region_name='us-east-1')
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

