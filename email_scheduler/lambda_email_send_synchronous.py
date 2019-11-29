import os
from botocore.exceptions import ClientError
from email_scheduler.mime.multipart import MIMEMultipart
from email_scheduler.mime.text import MIMEText
import os.path
from email_scheduler.mime.application import MIMEApplication
import boto3

def lambda_handler(event, context):

    def download_file_from_s3(bucket_name, filename):
        # filename = 'file1.png'
        resource = boto3.resource('s3')
        # bucket_name = 'lambda-ses2'
        my_bucket = resource.Bucket(bucket_name)
        key = filename
        local_filename = filename
        my_bucket.download_file(key, local_filename)
    
    
    def send_email_with_attachment_from_s3(bucket_name, filename, sender, recipient, subject, body_html):
        bucket_name = 'lambda-ses2'
        download_file_from_s3(bucket_name, filename)
    
        s3 = boto3.client("s3")
        print("Sender is <{}>".format(sender))
        sender = "Graphs For Good Service <" + sender + ">" 
        SENDER = sender
        # "Graphs For Good Service <armando.ordorica@mail.utoronto.ca>"
        RECIPIENT = recipient  # "armandordorica@gmail.com"
        AWS_REGION = "us-east-1"
        SUBJECT = subject  # "Graphs for Good - Here's your graph"
        ATTACHMENT = filename
    
        BODY_TEXT = body_html
    
        BODY_HTML = body_html
    
        # Graphs
        # for Good - Here's your graph
    
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
        print("att that works is type {}".format(type(att)))
    
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
    
    
    def direct_send_email_with_attachment_from_s3(bucket_name, filename, sender, recipient, subject, body_html):
    
        s3 = boto3.client("s3")
        sender = "Graphs For Good Service <" + sender + ">" 
        SENDER = sender
        # "Graphs For Good Service <armando.ordorica@mail.utoronto.ca>"
        RECIPIENT = recipient  # "armandordorica@gmail.com"
        AWS_REGION = "us-east-1"
        SUBJECT = subject  # "Graphs for Good - Here's your graph"
        # ATTACHMENT = filename
    
        BODY_TEXT = body_html
        BODY_HTML = body_html
    
        # Graphs
        # for Good - Here's your graph
    
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
        # print(type(get_object(bucket_name, filename)))
        s3_object_body = get_object(bucket_name, filename).read()
    
        #part = MIMEApplication(s3_object_body, filename)
        part = MIMEApplication(s3_object_body)
        
        # attachment
# if attachment_string:   # if bytestring available
#     part = MIMEApplication(str.encode('attachment_string'))
# else:    # if file provided
#     part = MIMEApplication(open(attachment_file.csv, 'rb').read())
# part.add_header('Content-Disposition', 'attachment', filename='name_of_attachment.csv')
# message.attach(part)


        part.add_header("Content-Disposition", 'attachment', filename=filename)
        msg.attach(part)
        ses_aws_client = boto3.client('ses', 'us-east-1')
        ses_aws_client.send_raw_email(RawMessage={"Data": msg.as_bytes()})
    
        msg.attach(msg_body)
    
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
            keys.append(key['Key'])
        return keys
    
    
    def get_object(bucket_name, object_name):
        """Retrieve an object from an Amazon S3 bucket
    
        :param bucket_name: string
        :param object_name: string
        :return: botocore.response.StreamingBody object. If error, return None.
        """
        # Retrieve the object
        s3 = boto3.client('s3')
        try:
            response = s3.get_object(Bucket=bucket_name, Key=object_name)
        except ClientError as e:
            # AllAccessDisabled error == bucket or object not found
            logging.error(e)
            return None
        # Return an open StreamingBody object
        return response['Body']
    
    
    def s3_to_email_multiple_emails(bucket_name, filename, sender, recipients, subject, body_html):
        for i in range(0, len(recipients)):
            direct_send_email_with_attachment_from_s3(bucket_name, filename, sender, recipients[i], subject, body_html)
            print("Email sent to {}".format(recipients[i]))
    
    
    
    ## Testing 
    # Look at emailParameters JSON to see the actual contents of the email 
    bucket_name = event['bucket_name']
    #filename = get_keys_from_s3(bucket_name)[0]
    filename = "armandordorica_gmail_com/armandordorica_gmail_com2019_11_29_06_28_20_358120/out/2019_11_29_01_25_53_203569_out.png"
    #filename = event['filename']
    sender = event['sender']
    recipients = event['recipients']
    subject = event['subject']
    body_html = event['body_html']
    
    print("bucket_name: {} with type: {} ".format(bucket_name, type(bucket_name)))
    print("filename: {} with type: {}".format(filename, type(filename)))
    print("sender: {} with type: {}".format(sender, type(sender)))
    print("recipients: {} with type: {}".format(recipients, type(recipients)))
    print("subjecte: {} with type: {}".format(subject, type(subject)))
    print("body_html: {} with type: {}".format(body_html, type(body_html)))
    
    
    s3_to_email_multiple_emails(bucket_name, filename, sender, recipients, subject, body_html)
    return {
        'statusCode': 200
        #'body': json.dumps('Hello from Lambda!')
    }
