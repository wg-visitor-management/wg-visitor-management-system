import os
import dotenv

from helpers.run_helper import get_stack_qualifier


dotenv.load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT")
S3_BUCKET_FOR_SAM = os.getenv("BUCKET_NAME")
JWT_SECRET = os.getenv("JWT_SECRET")
SENDER_EMAIL = os.getenv("ADMIN_EMAIL")
RECEIVER_MAILS = os.getenv("RECEIVER_MAILS")
APPLICATION_NAME = os.getenv("APP_NAME")
EMAIL_TEMPLATE = os.getenv("EMAIL_TEMPLATE")

SAM_STACK_NAME = f"{get_stack_qualifier('api-gateway')}"
BUCKET_NAME = f"{get_stack_qualifier('static-content-bucket')}"
USER_POOL_NAME = f"{get_stack_qualifier('user-pool')}"
USER_POOL_CLIENT_NAME = f"{get_stack_qualifier('user-pool-client')}"
TABLE_NAME = f"{get_stack_qualifier('database')}"
ROLE_NAME = f"{get_stack_qualifier('lambda-role-common')}"


def get_iam_stack(outputs):
    iam_stack = {
        "stack_name": "iam-policy",
        "template_body_url": "cfn/iam_policy.yaml",
        "parameters": [
            {
                "ParameterKey": "RoleName",
                "ParameterValue": ROLE_NAME,
            },
            {
                "ParameterKey": "Environment",
                "ParameterValue": ENVIRONMENT,
            },
            {"ParameterKey": "BucketArn", "ParameterValue": outputs["BucketArn"]},
            {
                "ParameterKey": "DynamoDBTableArn",
                "ParameterValue": outputs["DynamoDBTableArn"],
            },
            {
                "ParameterKey": "ApplicationName",
                "ParameterValue": APPLICATION_NAME,
            },
        ],
        "capabilities": ["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
    }
    return iam_stack


static_content_bucket_stack = {
    "stack_name": "static-content",
    "template_body_url": "cfn/static_content_bucket.yaml",
    "parameters": [
        {
            "ParameterKey": "BucketName",
            "ParameterValue": BUCKET_NAME,
        },
        {
            "ParameterKey": "Environment",
            "ParameterValue": ENVIRONMENT,
        },
        {
            "ParameterKey": "ApplicationName",
            "ParameterValue": APPLICATION_NAME,
        },
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
cognito_stack = {
    "stack_name": "cognito",
    "template_body_url": "cfn/cognito.yaml",
    "parameters": [
        {
            "ParameterKey": "Environment",
            "ParameterValue": ENVIRONMENT,
        },
        {
            "ParameterKey": "UserPoolName",
            "ParameterValue": USER_POOL_NAME,
        },
        {
            "ParameterKey": "UserPoolClientName",
            "ParameterValue": USER_POOL_CLIENT_NAME,
        },
        {
            "ParameterKey": "ApplicationName",
            "ParameterValue": APPLICATION_NAME,
        },
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
dynamodb_stack = {
    "stack_name": "dynamodb",
    "template_body_url": "cfn/dynamodb.yaml",
    "parameters": [
        {
            "ParameterKey": "Environment",
            "ParameterValue": ENVIRONMENT,
        },
        {
            "ParameterKey": "TableName",
            "ParameterValue": TABLE_NAME,
        },
        {
            "ParameterKey": "ApplicationName",
            "ParameterValue": APPLICATION_NAME,
        },
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
