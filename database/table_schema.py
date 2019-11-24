from __future__ import print_function # Python 2/3 compatibility
import boto3

#dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


table1 = dynamodb.create_table(
    TableName='Login_table',
    AttributeDefinitions=[
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        },
    ],
    KeySchema=[
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'  #Partition key
        },
    ],

    ProvisionedThroughput={
        'ReadCapacityUnits': 40,
        'WriteCapacityUnits': 40
    }
)


table2 = dynamodb.create_table(
    TableName='Graph_info',
    KeySchema=[
        {
            'AttributeName': 'Graph_Name',
            'KeyType': 'HASH'  #Partition key
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'Graph_Name',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 40,
        'WriteCapacityUnits': 40
    }
)
print("Table status:", table1.table_status)
print("Table status:", table2.table_status)