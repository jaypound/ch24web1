import boto3
import environ
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import logging

# def create_presigned_url(bucket_name, object_name, expiration=3600):
#     """Generate a pre-signed URL to upload a file to S3."""
#     s3_client = boto3.client('s3')
#     try:
#         response = s3_client.generate_presigned_url(
#             'put_object',
#             Params={
#                 'Bucket': bucket_name,
#                 'Key': object_name,
#                 # 'ContentType': content_type  # Remove this line
#             },
#             ExpiresIn=expiration
#         )
#         return response
#     except Exception as e:
#         print(f"Error generating pre-signed URL: {e}")
#         return None


# Load environment variables
env = environ.Env()
environ.Env.read_env()  # This loads variables from your .env file

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a pre-signed URL to upload a file to S3."""
    # Create an S3 client with credentials from the environment variables
    aws_access_key_id = env('AWS_ACCESS_KEY_ID', default=None)
    aws_secret_access_key = env('AWS_SECRET_ACCESS_KEY', default=None)
    aws_region = env('AWS_REGION', default='us-east-1')  # Optional default region

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name,
            },
            ExpiresIn=expiration
        )
        return response
    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error(f"Credentials error: {e}")
    except Exception as e:
        logging.error(f"Error generating pre-signed URL: {e}")
    return None




