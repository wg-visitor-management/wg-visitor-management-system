import logging

from configurations import config
from helpers.deploy_helpers import (
    deploy_stack,
    get_outputs,
    get_stack_outputs,
    run_command,
)
from helpers.run_helper import create_recursive_folders
from helpers.ses_helper import deploy_template, send_verification_mails, body_mail

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


outputs = {}

def deploy_api(outputs):
    """
    This function is used to deploy the SAM application
    """
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
        f"ReceiverMail={config.RECEIVER_MAILS} "
        f"JWTSecret={config.JWT_SECRET} "
        f"ApplicationName={config.APPLICATION_NAME}"
    )
    logger.info("Deploying SAM application...")
    run_command(deploy_command)


def install_requirements():
    """
    This function is used to install the requirements for the lambda functions
    """
    create_recursive_folders("../src", "common/python/lib/python3.11/site-packages")
    run_command(
        "python -m pip install -r ../requirements.txt --target ../src/common/python/lib/python3.11/site-packages"
    )


def main():
    deploy_stack(**config.static_content_bucket_stack)
    deploy_stack(**config.cognito_stack)
    outputs = deploy_stack(**config.dynamodb_stack)
    send_verification_mails(config.RECEIVER_MAILS, config.SENDER_EMAIL)
    outputs = deploy_stack(**config.get_iam_stack(outputs))
    outputs = get_outputs()
    install_requirements()
    deploy_api(outputs)
    get_stack_outputs(config.SAM_STACK_NAME)
    outputs = get_outputs()
    api_endpoint = outputs.get("VMSApiEndpoint")
    deploy_template(
        config.EMAIL_TEMPLATE,
        "A visitor needs your approval",
        body_mail,
        "A visitor needs your approval",
        api_endpoint,
    )

if __name__ == "__main__":
    main()
