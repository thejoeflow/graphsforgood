# Contains the operations needed for s3
import boto3

# assuming we have one and only one s3 bucket
bucket_name = 'shreyarajput'
bucket = boto3.resource('s3').Bucket(bucket_name)


def upload_file(filename, s3_name):
    ''' filename: string - filename of local file to upload
        s3_name: string - target key for the uploaded file (ex:tmp/usr/pie.png)
    '''
    bucket.upload_file(filename, s3_name)


def move_file(src, target):
    ''' src: string - key of s3 file to move
        target: string - key of s3 file to move to
    '''
    bucket.copy({'Bucket': bucket.name,
                 'Key': src},
                target)
    bucket.delete_objects(Delete={'Objects': [{'Key': src}]})


def delete_file(to_delete):
    ''' to_delete: string - key of s3 file to delete
    '''
    bucket.delete_objects(Delete={'Objects': [{'Key': to_delete}]})


upload_file('apple.csv', 'tmp/usr/pie.csv')