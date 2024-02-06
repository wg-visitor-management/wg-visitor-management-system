import os
import subprocess
import boto3
import logging
import dotenv
from cognito_operations import create_user_add_to_group
from ses_template import deploy_template, send_verification_mails, body_mail
dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client_cf = boto3.client("cloudformation")

outputs = {}
configurations = {
    "ADMIN_EMAIL" : os.getenv("ADMIN_EMAIL"),
    "ADMIN_CREDENTIALS" : os.getenv("ADMIN_CREDENTIALS"),
    "USER_CREDENTIALS" : os.getenv("USER_CREDENTIALS"),
    "ENVIRONMENT": os.getenv("ENVIRONMENT"),
    "S3_BUCKET_FOR_SAM": os.getenv("BUCKET_NAME"),
    "SAM_STACK_NAME": "api-gateway-lambda-sam",
    "BUCKET_NAME": "vms-static-content",
    "USER_POOL_NAME": "vms-user-pool",
    "USER_POOL_CLIENT_NAME": "vms-user-pool-client",
    "TABLE_NAME": "vms-database",
    "ROLE_NAME": "vms-lambda-role-common",
    "SENDER_EMAIL": "abhi22hada@gmail.com",
    "RECIPIENT_EMAIL": "abhi22hada@gmail.com",
    "JWT_SECRET": "vms-secret-key-1234",
}


def get_iam_stack(outputs, configurations=configurations):
    iam_stack = {
        "stack_name": "iam-stack",
        "template_body_url": "cfn/iam_policy.yaml",
        "parameters": [
            {
                "ParameterKey": "RoleName",
                "ParameterValue": configurations.get("ROLE_NAME"),
            },
            {
                "ParameterKey": "Environment",
                "ParameterValue": configurations.get("ENVIRONMENT"),
            },
            {"ParameterKey": "BucketArn", "ParameterValue": outputs["BucketArn"]},
            {
                "ParameterKey": "DynamoDBTableArn",
                "ParameterValue": outputs["DynamoDBTableArn"],
            },
        ],
        "capabilities": ["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
    }
    return iam_stack


static_content_bucket_stack = {
    "stack_name": "static-content-bucket-stack",
    "template_body_url": "cfn/static_content_bucket.yaml",
    "parameters": [
        {
            "ParameterKey": "BucketName",
            "ParameterValue": configurations.get("BUCKET_NAME"),
        },
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
cognito_stack = {
    "stack_name": "cognito-stack",
    "template_body_url": "cfn/cognito.yaml",
    "parameters": [
        {
            "ParameterKey": "Environment",
            "ParameterValue": configurations.get("ENVIRONMENT"),
        },
        {
            "ParameterKey": "UserPoolName",
            "ParameterValue": configurations.get("USER_POOL_NAME"),
        },
        {
            "ParameterKey": "UserPoolClientName",
            "ParameterValue": configurations.get("USER_POOL_CLIENT_NAME"),
        },
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
dynamodb_stack = {
    "stack_name": "dynamodb-stack",
    "template_body_url": "cfn/dynamodb.yaml",
    "parameters": [
        {
            "ParameterKey": "Environment",
            "ParameterValue": configurations.get("ENVIRONMENT"),
        },
        {
            "ParameterKey": "TableName",
            "ParameterValue": configurations.get("TABLE_NAME"),
        },
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
        exit(1)


def apigateway_lambda_deploy_sam():
    package_command = (
        "sam package "
        f"--s3-bucket {configurations.get('S3_BUCKET_FOR_SAM')} "
        "--template-file template.yaml "
        "--output-template-file ../gen/template-generated.yaml"
    )
    logger.info("Packaging SAM application...")
    run_command(package_command)

    deploy_command = (
        "sam deploy "
        "--template-file ../gen/template-generated.yaml "
        f"--stack-name {configurations.get('SAM_STACK_NAME')} "
        "--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM "
        f"--parameter-overrides Environment={configurations.get('ENVIRONMENT')} "
        f"BucketName={outputs.get('BucketName')} "
        f"DynamoDBTable={outputs.get('DynamoDBTableName')} "
        f"UserPoolId={outputs.get('UserPoolId')} "
        f"UserPoolClientId={outputs.get('UserPoolClientId')} "
        f"LambdaIAMRoleArn={outputs.get('LambdaIAMRoleArn')} "
        f"CognitoPoolArn={outputs.get('CognitoPoolArn')} "
        f"SenderMail={configurations.get('SENDER_EMAIL')} "
        f"ReceiverMail={configurations.get('RECIPIENT_EMAIL')} "
        f"JWTSecret={configurations.get('JWT_SECRET')}"
    )
    logger.info("Deploying SAM application...")
    run_command(deploy_command)

def install_requirements():
    run_command("mkdir -p ../src/common/python/lib/python3.11/site-packages")
    run_command("pip install -r ../requirements.txt --target ../src/common/python/lib/python3.11/site-packages")

def main():

    deploy_stack(**static_content_bucket_stack)
    deploy_stack(**cognito_stack)
    deploy_stack(**dynamodb_stack)
    deploy_template("vms_email_template-test", "A visitor needs your approval", body_mail, "A visitor needs your approval")
    send_verification_mails(configurations.get("ADMIN_EMAIL"))
    admin_credentials = configurations.get("ADMIN_CREDENTIALS")
    create_user_add_to_group(admin_credentials.get("name"), admin_credentials.get("email"), admin_credentials.get("password"), "admin")
    user_credentials = configurations.get("USER_CREDENTIALS")
    create_user_add_to_group(user_credentials.get("name"), user_credentials.get("email"), user_credentials.get("password"), "users")
    deploy_stack(**get_iam_stack(outputs))
    install_requirements()
    apigateway_lambda_deploy_sam()

if __name__ == "__main__":
    main()
