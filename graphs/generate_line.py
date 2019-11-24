import boto3
import os
import csv
import matplotlib.pyplot as plt


def generate_line(event):

    # extract arguments:
    filename = str()
    if 's3_filename' in event:
        filename = event['s3_filename']
        print('DEBUG - s3_filename=' + filename)
    else:
        print('ERROR - Must specify s3_filename')
        return 'ERROR'

    username = str()
    if 'username' in event:
        username = event['username']
        print('DEBUG - username=' + username)
    else:
        print('ERROR - Must specify username')
        return 'ERROR'

    upload_filename = 'tmp/'+username+'/line.png'

    title = str()
    if 'title' in event:
        title = event['title']
        print('DEBUG - title=' + title)
    else:
        title = None

    x_column = int()
    if 'colulmns' in event:
        x_column = event['x_column']
    else:
        print('ERROR - Must specify x_column to use for bar graph')
        return 'ERROR'

    y_column = list()
    if 'colulmns' in event:
        y_column = event['y_column']
    else:
        print('ERROR - Must specify y_column to use for bar graph')
        return 'ERROR'

    xlabel = str()
    if 'xlabel' in event:
        xlabel = event['xlabel']
    else:
        xlabel = None

    ylabel = str()
    if 'ylabel' in event:
        ylabel = event['ylabel']
    else:
        ylabel = None

    # S3 client
    s3 = boto3.resource('s3')
    buckets = list(s3.buckets.all())

    if len(buckets) < 1:
        print('ERROR: No available S3 bucket!')
        return 'ERROR'
    # again, assuming that there is only one bucket
    bucket = buckets[0]
    print('DEBUG - using S3 bucket "{}"'.format(bucket.name))
    bucket.download_file(filename, '/tmp/tmp.csv')

    # start parsing csv
    data = list()
    with open('/tmp/tmp.csv') as table:
        reader = csv.reader(table)
        for row in reader:
            data.append(row)

    # TODO: generate the graph

    # remove files from temporary storage
    os.remove('/tmp/tmp.csv')
    os.remove('/tmp/line.png')

    return upload_filename
