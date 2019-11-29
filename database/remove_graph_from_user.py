import boto3

dynamodb = boto3.client('dynamodb')
table_name = dynamodb.list_tables()['TableNames'][0]

def remove_graph_from_user(db, user_email, graph_id):
    # get user item from db
    resp = dynamodb.get_item(TableName=table_name,
            Key={'email': {'S': user_email}})

    # get graph attribute
    graphs = resp['Item']['graph']['M']

    # remove that specific graph entry
    graphs.pop(graph_id, None)

    # update the dynamodb entry
    ue = 'SET graph = :g'
    eav = {':g': {'M': graphs}}
    dynamodb.update_item(TableName=table_name, Key={'email':{'S': user_email}},
            UpdateExpression=ue, ExpressionAttributeValues=eav)
