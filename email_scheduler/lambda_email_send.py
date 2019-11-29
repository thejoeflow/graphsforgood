import json
import boto3


def lambda_handler(event, context):
    for i in event["Records"]:
        action = i["eventName"]
        ip = i["requestParameters"]["sourceIPAddress"]
        bucket_name = i["s3"]["bucket"]["name"]
        object = i["s3"]["object"]["key"]

    client = boto3.client("ses")

    subject = str(action) + 'Event from ' + bucket_name
    body = """
    <br>
    <h1>This email is to notify you regarding {} event.</h1>
    The object {} has been deleted
    Source IP: {}
    """.format(action, object, ip)

    message = {"Subject": {"Data": subject}, "Body": {"Html": {"Data": body}}}

    response = client.send_email(Source="armandordorica@gmail.com",
                                 Destination={"ToAddresses": ["armandordorica@gmail.com"]}, Message=message)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
