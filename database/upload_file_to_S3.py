import boto3
import datetime
bucket = list(boto3.resource('s3').buckets.all())[0]


def upload_file_inp(filename, email_add):

    '''
    Input:

    filename: input file name along with full file path
    email_add: current user logged in

    Output:

    InputFile_s3: Temporary file path of the given file in S3
    '''


    date_temp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
    date_temp = str(date_temp).replace(' ', '_').replace('/', '_').replace(':', '_').replace('.', '_')
    name = str(email_add).replace('@', '_').replace('.', '_')
    # target_temp = os.path.join('temp', name)
    file, ext = filename.rsplit('.', 1)
    InputFile_s3= 'temp'+ "/" + name + "/" + date_temp + "." + ext

    bucket.upload_file(filename, InputFile_s3)
    return InputFile_s3