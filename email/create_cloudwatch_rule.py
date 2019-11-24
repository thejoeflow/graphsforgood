import boto3


rule_name = 'Every 3 minutes'
scheduleExpression = "0 */2 * ? * *"


def create_cloudwatch_rule(rule_name, scheduleExpression):
    client = boto3.client('events')
    scheduleExpressionCRON = "cron({})".format(scheduleExpression)
    client.put_rule(Name=rule_name, ScheduleExpression=scheduleExpressionCRON, State='ENABLED')


rule_name = 'Every-3-minutes'
scheduleExpression = "0 */3 * ? * *"

create_cloudwatch_rule(rule_name, scheduleExpression);