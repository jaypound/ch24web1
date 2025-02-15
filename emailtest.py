import boto3
client = boto3.client('ses', region_name='us-east-1')
response = client.get_send_quota()
print(response)
