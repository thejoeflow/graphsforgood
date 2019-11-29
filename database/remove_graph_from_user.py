import boto3

dynamodb = boto3.client('dynamodb')
table_name = dynamodb.list_tables()['TableNames'][0]

def remove_graph_from_user(user_email, graph_id):
    # get user item from db
    resp = dynamodb.get_item(TableName=table_name,
            Key={'email': {'S': user_email}})

    # get graph attribute
    graphs = resp['Item']['graph']['M']

    # remove that specific graph entry
    item = graphs.pop(graph_id, None)

    # update the dynamodb entry
    ue = 'SET graph = :g'
    eav = {':g': {'M': graphs}}
    dynamodb.update_item(TableName=table_name, Key={'email':{'S': user_email}},
            UpdateExpression=ue, ExpressionAttributeValues=eav)

    # delete from s3
    if item is not None:
        to_delete = list()
        for k, v in enumerate(item):
            to_delete.append({'Key': v['inp']})
            to_delete.append({'Key': v['out']})

        s3 = boto3.resouce('s3')
        bucket = list(s3.buckets.all())[0]
        bucket.delete_objects(Delete={'Objects':to_delete})
