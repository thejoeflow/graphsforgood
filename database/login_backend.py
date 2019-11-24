import boto3
import random
import string
import json


from Crypto.Hash import SHA256
from boto3.dynamodb.conditions import Key, Attr


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


class User:

    def __init__(self, json_file):
        self.email = json_file.get('email')
        self.first_name = json_file.get('First Name')
        self.last_name =json_file.get('Last Name')
        self.password_hash = json_file.get('password_hash')
        self.salt = json_file.get('salt')

dynamodb = boto3.resource('dynamodb')

def sha256_hash_hex(data, salt=""):
    sha = SHA256.new()
    sha.update(data.encode("utf-8"))
    sha.update(salt.encode("utf-8"))
    return sha.hexdigest()


def salt_generator():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(10))



def create_new_user(email_add, first_name, last_name, password):
    """
        Registers and saves a new user with the given credentials to the database.
        :param username:
        :param password:
        :return: True if the user was registered successfully. False otherwise
        """
    salt = salt_generator()
    password_hash = sha256_hash_hex(password, salt)
    try:
        dynamoTable = dynamodb.Table('Login_table')
        dynamoTable.put_item(
            Item={
                'email': email_add,
                'First Name': first_name,
                'Last Name': last_name,
                'password_hash': password_hash,
                'salt': salt,
            }
        )
    except Exception as e:
        print("Failed to register user with email address provided: " + email_add, e, "\n")
        return False

create_new_user('test@gmail.com', 'shreya', 'rajput', 'password')

def get_user(email_add):
    try:
        dynamoTable = dynamodb.Table('Login_table')
        check = dynamoTable.query(
            KeyConditionExpression=Key('email').eq(email_add)
        )
        if len(check['Items']) is not 0:

            response = dynamoTable.get_item(
                Key={
                    'email':email_add,
                }
            )
            return response['Item']
        else:
            return False

    except Exception as e:
        print("Failed to retrieve user: " + email_add, e, "\n")
        return None


# response_user = get_user('dgdg@gmail.com')
# print(response_user.get('First Name'))



def authenticate(email, password):
    """
    Attempts to authenticate the user with the supplied credentials
    :param username:
    :param password:
    :return: True if user credentials are correct. False if authentication failed.
    """
    try:
        check = get_user(email)
        user = User(check)
        if check is not False:
            password_given = sha256_hash_hex(password, user.salt)
            return (email == user.email) & (password_given == user.password_hash)
        else:
            print("Email entered is not unique")
            return False
    except Exception as e:
        print("User authentication failed for user: " + email, e, "\n")
        return False






# create_new_user('shreya3243@gmail.com', 'molu', 'rajput', '1234')
# check = authenticate('shreya3243@gmail.com', '1234')
# print(check)