import boto3
import random
import string
import json
import datetime
import os


from Crypto.Hash import SHA256
from boto3.dynamodb.conditions import Key, Attr

def date_time():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")

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
        self.graph = json_file.get('graph')

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
                'graph': {},
            }
        )
    except Exception as e:
        print("Failed to register user with email address provided: " + email_add, e, "\n")
        return False


def register_new_graph(email_add, graph_name, email_list, Async_val, cron_sche, graph_type, graph_title, x_label, y_label, x_col, y_col, labels, subject, body, inputs3_temp_location, outputs3_temp_location):


    date_temp = date_time()
    date_temp = str(date_temp).replace(' ', '_').replace('/', '_').replace(':', '_').replace('.', '_')
    graph_id = str(email_add).replace('@', '_').replace('.', '_') + date_temp + str(graph_name)

    #move s3
    s3_inp_path, s3_out_path = move_file(inputs3_temp_location, outputs3_temp_location, graph_id, email_add)

    try:
        dynamoTable = dynamodb.Table('Login_table')
        dynamoTable.update_item(
        Key={
        'email': email_add,
        },
        UpdateExpression="set #Graph.#id = :name",
        ExpressionAttributeNames={
            '#Graph': 'graph',
            '#id': str(graph_id),
            # '#name': 'name',
            # '#subgraph': 'subgraph',
        },
        ExpressionAttributeValues = {
                ':name': {'graph_Name':graph_name,
                        'inp': s3_inp_path,
                        'out': s3_out_path,
                        'receiver_email': email_list,
                        'cron': cron_sche,
                        'Async': Async_val,
                        'Date': date_temp,
                        'subject': subject,
                        'body': body,
                        'config': {
                            'graph_type':graph_type,
                            'graph_title': graph_title,
                            'x_label': x_label,
                            'y_label': y_label,
                            'x_col': x_col,
                            'y_col': y_col,
                            'labels': labels,

                        }
                          },
            }
        )
        return graph_id
    except Exception as e:
        print("Failed to register user with email address provided: " + email_add, e, "\n")
        return False


email_add= 'shreya@gmail.com'
graph_name= 'vyhggjg'
# graph_id= 75647
s3_inp_path= '/user/shreya/file'
s3_out_path = '/user/shreya/out'
graph_type = 'bar'
email_list = ['armandordorica@gmail.com']
Async_val = True
cron_sche = '0/1 * 1/1 * ? *'
graph_type = 'bar'
graph_title = 'UC report'
x_label = 'frequncy'
y_label= 'car'
x_col = ['col1', 'col2', 'col3']
y_col= ['row1', 'row2', 'row3']
labels= ['bmw', 'tesla', 'jaguar']
subject = 'Hello from Graphs for Good'
body = 'Hi, there this your subscribed graph report. Enjoy'



# create_new_user(email_add, 'shreya', 'rajput', 'password')
given_id = register_new_graph(email_add, graph_name, s3_inp_path, s3_out_path, email_list, Async_val, cron_sche, graph_type, graph_title, x_label, y_label, x_col, y_col, labels, subject, body)
# 
print(given_id)




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


attribute = 'out'
def get_registered_graph(email_add, graph_id, attribute):
    user = get_user(email_add)
    user = User(user)
    return user.graph.get(str(graph_id)).get(attribute)


print(get_registered_graph('shreya@gmail.com', 'shreya_gmail_com2019_11_28_22_02_17_411953', attribute))


def get_all_graph(email_add):
    '''Returns array of all the graph id's present'''
    user = User(get_user(email_add))
    # user = User(check)
    value = user.graph
    # graphs = value.keys()
    dict ={}
    for key, value in value.items():

        dict.update({key: get_registered_graph(email_add, key, attribute)})
    return dict

# print(get_all_graph(email_add))
# get_registered_graph(email_add, graph_id, attribute)

# create_new_user('shreya3243@gmail.com', 'molu', 'rajput', '1234')
# check = authenticate('shreya3243@gmail.com', '1234')
# print(check)


bucket_name = 'shreyarajput'
bucket = boto3.resource('s3').Bucket(bucket_name)


def upload_file_inp(filename, email_add):


    date_temp = date_time()
    date_temp = str(date_temp).replace(' ', '_').replace('/', '_').replace(':', '_').replace('.', '_')
    name = str(email_add).replace('@', '_').replace('.', '_')
    # target_temp = os.path.join('temp', name)
    file, ext = filename.rsplit('.', 1)
    InputFile_s3= 'temp'+ "/" + name + "/" + date_temp + "." + ext
    ''' filename: string - filename of local file to upload
        s3_name: string - target key for the uploaded file (ex:tmp/usr/pie.png)
    '''
    bucket.upload_file(filename, InputFile_s3)
    return InputFile_s3


def upload_file_out(inp_file_name, out_filename, email_add):
    name = str(email_add).replace('@', '_').replace('.', '_')
    file, ext_temp = inp_file_name.rsplit('.', 1)
    out, ext = out_filename.rsplit('.', 1)
    Output_File_s3 = 'temp' + "/" + name + "/" + file + "_out" + "." + ext

    bucket.upload_file(out_filename, Output_File_s3)
    return Output_File_s3

# check = upload_file_inp('apple'
#                         '.csv', 'test@gmail.com')
# print(check)
# out = upload_file_out('2019_11_28_10_27_24_425159.csv', 'images.jpg', 'shreya@gmail.com')

def move_file(inp, out, graph_id, email_add):
    ''' src: string - key of s3 file to move
        target: string - key of s3 file to move to
    '''
    username = str(email_add).replace('@', '_').replace('.', '_')
    target_inp = username + "/" + str(graph_id) + "/" + 'inp' + "/" + inp.split('/')[2]
    bucket.copy({'Bucket': bucket.name,
                 'Key': inp},
                target_inp)
    bucket.delete_objects(Delete={'Objects': [{'Key': inp}]})

    target_out = username + "/" + str(graph_id) + "/" + 'out' + "/" + out.split('/')[2]
    bucket.copy({'Bucket': bucket.name,
                 'Key': out},
                target_out)
    bucket.delete_objects(Delete={'Objects': [{'Key': out}]})

    return target_inp, target_out


# print(move_file("temp/test_gmail_com/2019_11_28_10_27_09_887153.csv", "temp/test_gmail_com/2019_11_28_10_27_24_425159.csv", "test_gmail_com2019_11_28_02_22_44_718252", "test@gmail.com"))
# print(check)
# print(out)