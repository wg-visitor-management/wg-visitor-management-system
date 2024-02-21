import subprocess
import boto3
import logging

import config 
from run_helper import create_recursive_folders, get_stack_qualifier
from ses_template import deploy_template, send_verification_mails, body_mail

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client_cf = boto3.client("cloudformation")

 
outputs = {}

 
def get_iam_stack(outputs, ):
    iam_stack = {
        "stack_name": "iam-policy",
        "template_body_url": "cfn/iam_policy.yaml",
        "parameters": [
            {
                "ParameterKey": "RoleName",
                "ParameterValue": config.ROLE_NAME,
            },
            {
                "ParameterKey": "Environment",
                "ParameterValue": config.ENVIRONMENT,
            },
            {"ParameterKey": "BucketArn", "ParameterValue": outputs["BucketArn"]},
            {
                "ParameterKey": "DynamoDBTableArn",
                "ParameterValue": outputs["DynamoDBTableArn"],
            },
            {
                "ParameterKey": "ApplicationName",
                "ParameterValue": config.APPLICATION_NAME,
            }
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
            "ParameterValue": config.BUCKET_NAME,
        },
        {
            "ParameterKey": "Environment",
            "ParameterValue": config.ENVIRONMENT,
        },
        {
            "ParameterKey": "ApplicationName",
            "ParameterValue": config.APPLICATION_NAME,
        }
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
cognito_stack = {
    "stack_name": "cognito",
    "template_body_url": "cfn/cognito.yaml",
    "parameters": [
        {
            "ParameterKey": "Environment",
            "ParameterValue": config.ENVIRONMENT,
        },
        {
            "ParameterKey": "UserPoolName",
            "ParameterValue": config.USER_POOL_NAME,
        },
        {
            "ParameterKey": "UserPoolClientName",
            "ParameterValue": config.USER_POOL_CLIENT_NAME,
        },
        {
            "ParameterKey": "AppName",
            "ParameterValue": config.APPLICATION_NAME,
        }
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
dynamodb_stack = {
    "stack_name": "dynamodb",
    "template_body_url": "cfn/dynamodb.yaml",
    "parameters": [
        {
            "ParameterKey": "Environment",
            "ParameterValue": config.ENVIRONMENT,
        },
        {
            "ParameterKey": "TableName",
            "ParameterValue": config.TABLE_NAME,
        },
        {
            "ParameterKey": "ApplicationName",
            "ParameterValue": config.APPLICATION_NAME,
        }
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
 
 
def extract_outputs(response):
    for output in response["Stacks"][0]["Outputs"]:
        outputs[output["OutputKey"]] = output["OutputValue"]
 
 
def get_stack_outputs(stack_name):
    try:
        response = client_cf.describe_stacks(StackName=stack_name)
        extract_outputs(response)
    except Exception as error:
        logger.error(f"Error describing stack: {stack_name}")
        logger.error(error)
        return False
    else:
        logger.info(f"Stack: {stack_name} exists!")
        return True
 
 
def deploy_stack(stack_name, template_body_url, parameters, capabilities):
    logger.info("Deploying stack: {} wiht params : {}".format(stack_name, parameters))
    template_body = open(template_body_url).read()
    logger.info(f"Deploying stack: {stack_name}\n")
    stack_name = get_stack_qualifier(stack_name)
 
    try:
        if not get_stack_outputs(stack_name):
            response = client_cf.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=capabilities,
            )
        else:
            response = client_cf.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=capabilities,
            )
    except Exception as error:
        logger.error(error)
    finally:
        logger.info(f"Waiting for stack: {stack_name} to be deployed...")
        waiter = client_cf.get_waiter("stack_create_complete")
        waiter.wait(
            StackName=stack_name, WaiterConfig={"Delay": 10, "MaxAttempts": 100}
        )
        logger.info(f"Stack: {stack_name} deployed successfully!")
        get_stack_outputs(stack_name)
 
 
def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)  
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
 
 
def apigateway_lambda_deploy_sam():
    package_command = (
        "sam package "
        f"--s3-bucket {config.S3_BUCKET_FOR_SAM} "
        "--template-file template.yaml "
        "--output-template-file template-generated.yaml"
    )
    logger.info("Packaging SAM application...")
    run_command(package_command)
 
    deploy_command = (
        "sam deploy "
        "--template-file template-generated.yaml "
        f"--stack-name {config.SAM_STACK_NAME} "
        "--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM "
        f"--parameter-overrides Environment={config.ENVIRONMENT} "
        f"BucketName={outputs.get('BucketName')} "
        f"DynamoDBTable={outputs.get('DynamoDBTableName')} "
        f"UserPoolId={outputs.get('UserPoolId')} "
        f"UserPoolClientId={outputs.get('UserPoolClientId')} "
        f"LambdaIAMRoleArn={outputs.get('LambdaIAMRoleArn')} "
        f"CognitoPoolArn={outputs.get('CognitoPoolArn')} "
        f"SenderMail={config.SENDER_EMAIL} "
        f"ReceiverMail={config.RECIPIENT_EMAIL} "
        f"JWTSecret={config.JWT_SECRET} "
        f"ApplicationName={config.APPLICATION_NAME}"
    )
    logger.info("Deploying SAM application...")
    run_command(deploy_command)
 
 
def install_requirements():
 
    create_recursive_folders("../src", "common/python/lib/python3.11/site-packages")
   
    run_command(
        "pip install -r ../requirements.txt --target ../src/common/python/lib/python3.11/site-packages"
    )
 
 
def main():
 
    deploy_stack(**static_content_bucket_stack)
    deploy_stack(**cognito_stack)
    deploy_stack(**dynamodb_stack)
    send_verification_mails(config.ADMIN_EMAIL)
    deploy_stack(**get_iam_stack(outputs))
    install_requirements()
    apigateway_lambda_deploy_sam()
    get_stack_outputs(config.SAM_STACK_NAME)
    APIGatewayEndpoint = outputs.get("VMSApiEndpoint")
    deploy_template(
        "vms_email_template-test",
        "A visitor needs your approval",
        body_mail,
        "A visitor needs your approval",
        APIGatewayEndpoint
    )
 
if __name__ == "__main__":
    main()