import configparser
import boto3
import json

# Read AWS credentials from the config file
cfg_data = configparser.ConfigParser()
cfg_data.read('dl.cfg')

# Save AWS credentials
access_key_id = cfg_data['AWS']['access_key_id']
secret_access_key = cfg_data['AWS']['secret_access_key']

# Save IAM role and IAM policy data
role_name = cfg_data["IAM"]["role_name"]
policy_name = cfg_data["IAM"]["policy_name"]

# Create IAM client
iam = boto3.client(
    'iam',
    region_name='us-east-1',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key
)