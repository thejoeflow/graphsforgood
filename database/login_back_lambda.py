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
import boto3
import random
import string

from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
dynamoTable = dynamodb.Table('Login_table')

def lambda_handler(event, context):
    try:
        check = dynamoTable.query(
            KeyConditionExpression=Key('email').eq(event['email_add'])
        )
        if len(check['Items']) is not 0:

            response = dynamoTable.get_item(
                Key={
                    'email':event['email_add'],
                }
            )
            return response['Item']
        else:
            return False
    except Exception as e:
        print("Failed to retrieve user: " + event['email_add'], e, "\n")
        return {
            'statusCode': 500,
            'body': json.dumps("Oops! Something went wrong.")
            }

"""
expected Input:
{
  "email_add": "shreya3243@gmail.com"
}
       """