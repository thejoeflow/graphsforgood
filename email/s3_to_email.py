import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os.path

from email.mime.application import MIMEApplication

import boto3


def download_file_from_s3(bucket_name, filename):
    # filename = 'file1.png'
    resource = boto3.resource('s3')
    # bucket_name = 'lambda-ses2'
    my_bucket = resource.Bucket(bucket_name)
    key = filename
    local_filename = filename
    my_bucket.download_file(key, local_filename)


def send_email_with_attachment_from_s3(filename):
    bucket_name = 'lambda-ses2'
    download_file_from_s3(bucket_name, filename)

    s3 = boto3.client("s3")
    SENDER = "Graphs For Good Service <armando.ordorica@mail.utoronto.ca>"
    RECIPIENT = "armandordorica@gmail.com"
    AWS_REGION = "us-east-1"
    SUBJECT = "Graphs for Good - Here's your graph"
    ATTACHMENT = filename

    BODY_TEXT = "Hello,\r\nPlease see the attached file for a list of customers to contact."

    BODY_HTML = """
    <html>
    <head></head>
    <body>
    <h1>Hello!</h1>
    <p>Please see the attached file for a list of customers to contact.</p>
    </body>
    </html>
    """

    CHARSET = "utf-8"
    client = boto3.client('ses', region_name=AWS_REGION)

    msg = MIMEMultipart('mixed')
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER
    msg['To'] = RECIPIENT

    msg_body = MIMEMultipart('alternative')
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    att = MIMEApplication(open(ATTACHMENT, 'rb').read())

    att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(ATTACHMENT))

    msg.attach(msg_body)

    msg.attach(att)
    print(msg)
    try:
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=[
                RECIPIENT
            ],
            RawMessage={
                'Data': msg.as_string(),
            },
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def get_keys_from_s3(s3_bucket_name):
    from boto3 import client
    conn = client('s3')
    keys = []
    for key in conn.list_objects(Bucket=s3_bucket_name)['Contents']:
        #print(key['Key'])
        keys.append(key['Key'])
    return keys


bucket_name = 'lambda-ses2'

# download_file_from_s3(bucket_name, filename)
# send_email_with_attachment_from_local('file2.png');

filename = get_keys_from_s3(bucket_name)[1]
send_email_with_attachment_from_s3(filename)


