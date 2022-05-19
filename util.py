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
policy_arn = cfg_data["IAM"]["policy_arn"]

# Create IAM client
iam = boto3.client(
    'iam',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key
)

# Create Redshift client
redshift = boto3.client(
    'redshift',
    region_name='us-east-1',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key
)

cluster_identifier = cfg_data["Redshift"]["cluster_identifier"]


def create_iam_role():
    """ Create IAM role """
    try:
        role = iam.create_role(
            RoleName=role_name,
            Description="Allows Redshift cluster to call AWS services on behalf of the user",
            AssumeRolePolicyDocument=json.dumps(
                {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "redshift.amazonaws.com"
                            }
                        }
                    ],
                    "Version": "2012-10-17"
                }
            )
        )
        print("Role named {} has been created".format(role_name))
        role_arn = iam.get_role(RoleName=role_name)["Role"]["Arn"]
        print("Role {}'s ARN is: {}".format(role_name, role_arn))

    except Exception as e:
        print(str(e))


def extract_role_arn():
    role_arn = iam.get_role(
        RoleName=role_name
    )["Role"]["Arn"]
    return role_arn


def create_policy():
    """ Create a policy to be attached to the 'loadDataFromS3ToRedshift' role """
    try:
        policy = iam.create_policy(
            PolicyName=policy_name,
            Description="Allow to list and access content of the target bucket 'tray-log-streaming'",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "s3:ListBucket"
                            ],
                            "Resource": [
                                "arn:aws:s3:::tray-log-streaming"
                            ]
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "s3:PutObject",
                                "s3:GetObject",
                                "s3:DeleteObject",
                            ],
                            "Resource": [
                                "arn:aws:s3:::tray-log-streaming/*"
                            ]
                        }
                    ]
                }
            )
        )
        print("Policy named '{}' created.".format(policy_name))
        policy_arn = policy["Policy"]["Arn"]
        print("Policy named '{}' has ARN '{}'".format(policy_name, policy_arn))
    except Exception as e:
        print(str(e))


def attach_policy():
    try:
        attachment = iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        print("Policy named {} attached to role {}.".format(policy_name, role_name))
    except Exception as e:
        print(str(e))


def extract_cluster_info():
    clusters = redshift.describe_clusters(
        ClusterIdentifier=cluster_identifier
    )["Clusters"]

    target = None

    for cluster in clusters:
        if cluster["ClusterIdentifier"] == cluster_identifier:
            target = cluster

    cluster_endpoint = target["Endpoint"]["Address"]
    vpc_security_group_id = target["VpcSecurityGroups"][0]["VpcSecurityGroupsId"]

    print("Cluster '{}' endpoint is '{}'".format(cluster_identifier, cluster_endpoint))
    print("Cluster '{}''s VPC security group ID is '{}'".format(cluster_identifier, vpc_security_group_id))

