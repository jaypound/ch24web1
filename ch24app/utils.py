import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import logging

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a pre-signed URL to upload a file to S3."""
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name,
                # 'ContentType': content_type  # Remove this line
            },
            ExpiresIn=expiration
        )
        return response
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return None




