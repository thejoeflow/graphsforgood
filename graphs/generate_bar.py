import boto3
import os
import csv
import numpy
import matplotlib.pyplot as plt


def generate_bar(event):
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
    upload_filename = 'tmp/' + username + '/bar.png'

    title = str()
    if 'title' in event:
        title = event['title']
        print('DEBUG - title=' + title)
    else:
        title = None

    columns = list()
    if 'columns' in event:
        columns = event['columns']
    else:
        print('ERROR - Must specify columns to use for bar graph')
        return 'ERROR'

    xlabel = list()
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

    # process data a bit:
    if xlabel is not None:
        # treat first row as xlabel
        for i in columns:
            xlabel.append(data[0][i])
    else:
        data.pop(0)

    # convert from string to float
    values = list()
    for i in columns:
        x = data[1][i].strip()
        if not x.isnumeric():
            values.append(0.0)
        else:
            values.append(float(x))

    # Plot the graph
    if ylabel is not None:
        plt.ylabel(ylabel)

    x = list(numpy.arange(len(columns)))

    plt.bar(x, values)
    plt.xticks(x, xlabel)

    if title is not None:
        plt.title(title)

    plt.savefig('/tmp/bar.png', format='png')

    bucket.upload_file('/tmp/bar.png', upload_filename)

    # remove files from temporary storage
    os.remove('/tmp/tmp.csv')
    os.remove('/tmp/bar.png')

    return upload_filename