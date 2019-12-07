import boto3
import os
import csv
import numpy
import matplotlib.pyplot as plt


def generate_line(event):
    # extract arguments:
    filename = str()
    if 's3_filename' in event:
        filename = event['s3_filename']
    else:
        print('ERROR - Must specify s3_filename')
        return 'ERROR'

    username = str()
    if 'username' in event:
        username = event['username']
    else:
        print('ERROR - Must specify username')
        return 'ERROR'

    upload_filename = filename.rsplit('.', 1)[0] + "_out.png"

    title = str()
    if 'title' in event:
        title = event['title']
    else:
        title = None

    x_column = int()
    if 'x_column' in event:
        x_column = event['x_column']
    else:
        print('ERROR - Must specify x_column to use for bar graph')
        return 'ERROR'

    y_column = list()
    if 'y_column' in event:
        y_column = event['y_column']
        if len(y_column) < 1:
            print('ERROR - y_column must not be empty')
            return 'ERROR'

        if len(y_column) > 7:
            print('WARNING - capping y_column to first 7 values')
            y_column = y_column[:7]
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

    x_constraint = list()
    if 'x_constraint' in event:
        x_constraint = event['x_constraint']
    else:
        x_constraint = None

    # S3 client -------------------------------------------------
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('lambda-ses-a3')
    bucket.download_file(filename, '/tmp/tmp.csv')

    # start parsing csv
    data = list()
    with open('/tmp/tmp.csv') as table:
        reader = csv.reader(table)
        for row in reader:
            data.append(row)

    # get the labels
    labels = data.pop(0)
    if xlabel is None:
        xlabel = labels[x_column]
    if ylabel is None:
        ylabel = labels[y_column[0]]

    # get the legend from this as well
    legends = list()
    for i in y_column:
        legends.append(labels[i])

    # transpose the data such that each sub-array is a column
    data = numpy.transpose(data).tolist()

    values = list()
    # convert from string to float to plot
    while (len(data) > 0):
        row = data.pop(0)
        temp = list()
        for cell in row:
            cell = cell.strip()
            if not cell.isnumeric():
                temp.append(0.0)
            else:
                temp.append(float(cell))
        values.append(temp)

    plt.grid()
    if x_constraint is not None:
        plt.xlim(x_constraint)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # plot every specified column
    for i in y_column:
        plt.plot(values[x_column], values[i])

    plt.legend(legends)

    if title is not None:
        plt.title(title)

    plt.savefig('/tmp/line.png', format='png')

    # upload to S3
    bucket.upload_file('/tmp/line.png', upload_filename)

    plt.clf()

    # remove files from temporary storage
    os.remove('/tmp/tmp.csv')
    os.remove('/tmp/line.png')

    return upload_filename
