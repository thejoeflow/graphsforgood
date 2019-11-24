import boto3
import s3fs

s3 = boto3.resource('s3')

bucket_name = 'lambda-ses2'

fs = s3fs.exitS3FileSystem(anon=False)
items = fs.ls(bucket_name)
object_name = items[0]


s3 = boto3.client('s3')
s3.download_file(bucket_name, object_name, str(items[0]))


import boto3
filename = 'file1.png'
resource = boto3.resource('s3')
bucket_name = 'lambda-ses2'
my_bucket = resource.Bucket(bucket_name)
key = filename
local_filename = filename
my_bucket.download_file(key, local_filename)
