import boto3
import os
import csv
import matplotlib.pyplot as plt


def generate_pie(event):

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

    title = str()
    if 'title' in event:
        title = event['title']
        print('DEBUG - title=' + title)
    else:
        title = None

    labels = list()
    if 'labels' in event:
        labels = event['labels']
    else:
        labels = None

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

    # if labels not specified in input, take from first row
    if labels is None:
        labels = data[0]

    # assuming there is only one row of data for now
    values = list()
    for x in data[1]:
        x = x.strip()
        if not x.isnumeric():
            print('WARNING - non-numeric item in csv! Treating as 0.')
            values.append(0.0)
        else:
            values.append(float(x))

    # normalize data
    total = sum(values)
    for i in range(len(values)):
        values[i] /= total

    # plot the data
    plt.pie(values, labels=labels, shadow=True, autopct='%1.1f%%')
    if title is not None:
        plt.title(title)
    plt.savefig('/tmp/pie.png', format='png')

    # upload to s3
    upload_filename = filename.rsplit('.', 1)[0] + "_out.png"
    bucket.upload_file('/tmp/pie.png', upload_filename)

    # remove files from temporary storage
    os.remove('/tmp/tmp.csv')
    os.remove('/tmp/pie.png')

    return upload_filename
