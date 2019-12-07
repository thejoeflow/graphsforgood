"""
Function1: Create_user()
       Registers and saves a new user with the given credentials to the database.
       :param username:
       :param password:
       :return: True if the user was registered successfully. False otherwise
       """


import json
import boto3


dynamodb = boto3.resource('dynamodb')
dynamoTable = dynamodb.Table('Login_table')


def lambda_handler(event, context):
    try:

        dynamoTable.put_item(
            Item={
                'email': event['email_add'],
                'First Name': event['first_name'],
                'Last Name': event['last_name'],
                'password_hash': event['password_hash'],
                'salt': event['salt'],
                'graph': {},
            }

        )
        return {
            'statusCode': 200,
            'body': json.dumps("Created new table!")
        }
    except Exception as e:
        print("Failed to register user with email address provided: " + event['email_add'], e, "\n")
        return {
            'statusCode': 500,
            'body': json.dumps("Oops! Something went wrong.")
        }

"""
expected Input:
       {
  "email_add": "user3@gmail.com",
  "first_name": "blind",
  "last_name": "user",
  "password_hash": "welcome123",
  "salt": "welcome123"
}
       """


"""
Function2 : get_user()
       Returns false if user doesn't exist.
       Else returns dictionary of the given user's(email address provided) 
       Dictionary items/attributes returned: First name, Last name, email, password, salt.
       """

import json
import urllib.parse
import boto3

print('Loading function')

bucket_name = 'shreyarajput'
bucket = boto3.resource('s3').Bucket(bucket_name)


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    # bucket = event['Records'][0]['s3']['bucket']['name']
    # key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        username = str(event['email_add']).replace('@', '_').replace('.', '_')
        target_inp = username + "/" + str(event['graph_id']) + "/" + 'inp' + "/" + event['inp'].split('/')[2]
        bucket.copy({'Bucket': bucket.name,
                     'Key': event['inp']},
                    target_inp)
        bucket.delete_objects(Delete={'Objects': [{'Key': event['inp']}]})

        target_out = username + "/" + str(event['graph_id']) + "/" + 'out' + "/" + event['out'].split('/')[2]
        bucket.copy({'Bucket': bucket.name,
                     'Key': event['out']},
                    target_out)
        bucket.delete_objects(Delete={'Objects': [{'Key': event['out']}]})

        return target_inp, target_out


    except Exception as e:
        return False

"""
expected Input:
{
  "email_add": "shreya3243@gmail.com"
}
       """




"""
Function3: move_temp_toPermanent()
        Moves data from temp folder in S3 to permanent directory( "user_name\graph_id\inp\file" and "user_name\graph_id\out\file_out")
       :returns: permanent/final path for both input and out file
       :output example:  "shreya_gmail_com/test_gmail_com2019_11_28_02_22_44_718252/inp/2019_11_27_16_06_49_262655.csv",
                         "shreya_gmail_com/test_gmail_com2019_11_28_02_22_44_718252/out/2019_11_28_10_27_24_425159_out.jpg"
       """

import json
import urllib.parse
import boto3

print('Loading function')

bucket_name = 'shreyarajput'
bucket = boto3.resource('s3').Bucket(bucket_name)


def lambda_handler(event, context):
    returndata = dict()
    try:
        username = str(event['email_add']).replace('@', '_').replace('.', '_')
        target_inp = username + "/" + str(event['graph_id']) + "/" + 'inp' + "/" + event['inp'].split('/')[2]
        bucket.copy({'Bucket': bucket.name,
                     'Key': event['inp']},
                    target_inp)
        bucket.delete_objects(Delete={'Objects': [{'Key': event['inp']}]})

        target_out = username + "/" + str(event['graph_id']) + "/" + 'out' + "/" + event['out'].split('/')[2]
        bucket.copy({'Bucket': bucket.name,
                     'Key': event['out']},
                    target_out)
        bucket.delete_objects(Delete={'Objects': [{'Key': event['out']}]})

        returndata['in'] = target_inp
        returndata['out'] = target_out

        return returndata


    except Exception as e:
        returndata['Error'] = str(e)
        return json.dumps(returndata)


'''
expected Input:
{
  "inp": "temp/shreya_gmail_com/2019_11_27_16_06_49_262655.csv", #(Temporary input file path)
  "out": "temp/shreya_gmail_com/2019_11_28_10_27_24_425159_out.jpg", #(Temporary ouput file path)
  "email_add": "shreya@gmail.com",
  "graph_id": "test_gmail_com2019_11_28_02_22_44_718252"
}
'''



"""
Function4: register_new_graph()
       Creates a unique graph_id. Then moves temporary files to permanent.
       With graph id as key it updates the form data in the database and generates the graph.
       
       :returns: the unique Graph_id
       """
import json
import boto3
import random
import string
import datetime

dynamodb = boto3.resource('dynamodb')
dynamoTable = dynamodb.Table('Login_table')
lambda_client = boto3.client('lambda')


def lambda_handler(event, context):
    date_temp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
    date_temp = str(date_temp).replace(' ', '_').replace('/', '_').replace(':', '_').replace('.', '_')
    graph_id = str(event['email_add']).replace('@', '_').replace('.', '_') + date_temp

    returnval = dict()
    try:
        x = {"inp": event['inp'], "out": event['out'], "email_add": event['email_add'], "graph_id": graph_id}
        resp = lambda_client.invoke(FunctionName="move_temp_toPermanent", InvocationType='RequestResponse',
                                    Payload=json.dumps(x))
        s = resp['Payload'].read().decode("utf-8")
        s = s.replace('\\', '')
        invoke = json.loads(s)

        if 'Error' in invoke:
            returnval['Error'] = 'Error reading file'
            return json.dump(returnval)

        else:

            s3_inp_path = invoke.get('in')
            s3_out_path = invoke.get('out')

            dynamoTable = dynamodb.Table('Login_table')
            dynamoTable.update_item(
                Key={
                    'email': event['email_add'],
                },
                UpdateExpression="set #Graph.#id = :name",
                ExpressionAttributeNames={
                    '#Graph': 'graph',
                    '#id': str(graph_id),
                    # '#name': 'name',
                    # '#subgraph': 'subgraph',
                },
                ExpressionAttributeValues={
                    ':name': {'graph_Name': event['graph_name'],
                              'inp': str(s3_inp_path),
                              'out': str(s3_out_path),
                              'receiver_email': event['email_list'],
                              'cron': event['cron_sche'],
                              'Async': event['Async_val'],
                              'Date': date_temp,
                              'body': event['body'],
                              'subject': event['subject'],
                              'config': {
                                  'graph_type': event['graph_type'],
                                  'graph_title': event['graph_title'],
                                  'x_label': event['x_label'],
                                  'y_label': event['y_label'],
                                  'x_col': event['x_col'],
                                  'y_col': event['y_col'],
                                  'labels': event['labels'],

                              }
                              },
                }
            )

        return graph_id



    except Exception as e:
        print(e)
        print("Failed to register user with email address provided: " + event['email_add'], e, "\n")
        raise e


'''
expected Input:
{
  "inp": "temp/shreya_gmail_com/2019_11_27_16_06_49_262655_out.jpg", #(Temporary input file path)
  "out": "temp/shreya_gmail_com/2019_11_27_19_55_38_668671.csv",  #(Temporary output file path)
  "email_add": "shreya@gmail.com", 
  "graph_name": "graph1",
  "graph_type": "bar",
  "email_list": [
    "armandordorica@gmail.com",
    "armando.ordorica@mail.utoronto.ca",
    "thejoeflow@gmail.com"
  ],
  "Async_val": true,
  "cron_sche": "0/1 * 1/1 * ? *",
  "graph_title": "UC report",
  "subject": "graph",
  "body": "here is your graph",
  "x_label": "frequncy",
  "y_label": "car",
  "x_col": int,
  "y_col": [
    "row1",
    "row2",
    "row3"
  ],
  "labels": [
    "bmw",
    "tesla",
    "jaguar"
  ]
}
'''
"""
Function5: get_registered_graph()
       input: email, graph_id and graph attribute that you need.

       :returns: Returns the specfied attribut
       """

import json
import boto3
import random
import string
import datetime

dynamodb = boto3.resource('dynamodb')
dynamoTable = dynamodb.Table('Login_table')
lambda_client = boto3.client('lambda')


def lambda_handler(event, context):
    try:
        x = {"email_add": event['email_add']}
        invoke = lambda_client.invoke(FunctionName="get_user", InvocationType='RequestResponse', Payload=json.dumps(x))

        user = json.loads(invoke['Payload'].read().decode("utf-8"))
        user = user.get('body').get("graph").get(str(event['graph_id'])).get(event['attribute'])

        return user

    except Exception as e:
        print(e)
        print("Failed to get information about user with email address provided: " + event['email_add'], e, "\n")
        raise e


'''
expected Input:
{
  "email_add": "shreya@gmail.com",
  "graph_id": "shreya_gmail_com2019_11_29_03_43_08_823502",
  "attribute": "config"
}
'''

"""
Function6: get_all_graph_config()
       input: email .

       :returns: Returns the graph config for all the graph_id's in json format.
       """

import json
import boto3
import random
import string
import datetime

dynamodb = boto3.resource('dynamodb')
dynamoTable = dynamodb.Table('Login_table')
lambda_client = boto3.client('lambda')


def lambda_handler(event, context):
    try:
        x = {"email_add": event['email_add']}
        invoke = lambda_client.invoke(FunctionName="get_user", InvocationType='RequestResponse', Payload=json.dumps(x))
        user = json.loads(invoke['Payload'].read().decode("utf-8"))

        user = user.get('body')
        value = user.get('graph')

        dict = {}

        for key, value in value.items():
            get_registered_graph = user.get('graph').get(str(key)).get(event['attribute'])
            dict.update({key: get_registered_graph})

        return json.dumps(dict)

    except Exception as e:
        print(e)
        print("Failed to get information about user with email address provided: " + event['email_add'], e, "\n")
        raise e


'''
expected Input:
{
  "email_add": "shreya@gmail.com"
}
'''

"""
Function6: delete_single_graph()
       input: email and graph id.

       :returns: deletes graph from s3 and database.
       """

import json
import boto3
import random
import string
import datetime

dynamodb = boto3.resource('dynamodb')

bucket_name = 'lambda-ses-a3'
bucket = boto3.resource('s3').Bucket(bucket_name)


def lambda_handler(event, context):
    try:
        dynamoTable = dynamodb.Table('Login_table')
        resp = dynamoTable.get_item(
            Key={
                'email': event['email_add'],
            }
        )

        graphs = resp['Item'].get('graph')

        bucket.delete_objects(Delete={'Objects': [{'Key': graphs.get(event['graph_id']).get('inp')}]})
        bucket.delete_objects(Delete={'Objects': [{'Key': graphs.get(event['graph_id']).get('out')}]})
        # # remove that specific graph entry

        graphs.pop(event['graph_id'], None)

        # # update the dynamodb entry
        ue = 'SET graph = :g'
        eav = {':g': graphs}
        dynamoTable.update_item(Key={
            'email': event['email_add'],
        },
            UpdateExpression=ue,
            ExpressionAttributeValues=eav)

        return {
            'statusCode': 200,
            'body': json.dumps("Deleted graph with id" + event['graph_id'])

        }

    except Exception as e:
        print("Failed to register user with email address provided: " + event['email_add'], e, "\n")
        return {
            'statusCode': 500,
            'body': json.dumps("Oops! Something went wrong. Files are missing in either s3 bucket or Database")
        }

'''
expected Input:
{
  
  "email_add": "user1@gmail.com",
  "graph_id": "user1_gmail_com2019_12_07_01_33_58_995375"
}

'''