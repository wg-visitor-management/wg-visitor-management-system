import subprocess
import boto3
import logging
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client_cf = boto3.client("cloudformation")

env_variables = {
    "stage_name": config.STAGE_NAME,
    "stack_name": "api-gateway-lambda-sam",
    "s3_bucket": config.BUCKET_NAME,
}
cognito_stack = {
    "stack_name": "cognito-stack",
    "template_body_url": "cfn/cognito.yaml",
    "parameters": [
        {"ParameterKey": "Stage", "ParameterValue": env_variables.get("stage_name")},
        {"ParameterKey": "UserPoolName", "ParameterValue": "vms-user-pool"},
        {
            "ParameterKey": "UserPoolClientName",
            "ParameterValue": "vms-user-pool-client",
        },
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
dynamodb_stack = {
    "stack_name": "dynamodb-stack",
    "template_body_url": "cfn/dynamodb.yaml",
    "parameters": [
        {"ParameterKey": "Stage", "ParameterValue": env_variables.get("stage_name")},
        {"ParameterKey": "TableName", "ParameterValue": "vms-database"},
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
iam_stack = {
    "stack_name": "iam-stack",
    "template_body_url": "cfn/iam_policy.yaml",
    "parameters": [
        {"ParameterKey": "Stage", "ParameterValue": env_variables.get("stage_name")},
        {"ParameterKey": "RoleName", "ParameterValue": "vms-lambda-role-common"},
    ],
    "capabilities": ["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
}

static_content_bucket_stack = {
    "stack_name": "static-content-bucket-stack",
    "template_body_url": "cfn/static_content_bucket.yaml",
    "parameters": [
        {"ParameterKey": "BucketName", "ParameterValue": "vms-static-content-test"}
    ],
    "capabilities": ["CAPABILITY_IAM"],
}


def deploy_stack(stack_name, template_body_url, parameters, capabilities, action):
    template_body = open(template_body_url).read()
    logger.info(f"Creating stack: {stack_name}\n")
    try:
        if action == "create":
            response = client_cf.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=capabilities,
            )
        elif action == "update":
            response = client_cf.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=capabilities,
            )
    except Exception as error:
        logger.error(f"Error creating stack: ")
        logger.error(error)
    else:
        logger.info(f"Waiting for stack: {stack_name} to be created...")
        waiter = client_cf.get_waiter("stack_create_complete")
        waiter.wait(
            StackName=stack_name, WaiterConfig={"Delay": 10, "MaxAttempts": 100}
        )
        logger.info(f"Stack: {stack_name} created successfully!")

        return response


def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
        exit(1)


def apigateway_lambda_deploy_sam():
    package_command = (
        "sam package "
        f"--s3-bucket {env_variables.get('s3_bucket')} "
        "--template-file template.yaml "
        "--output-template-file gen/template-generated.yaml"
    )
    logger.info("Packaging SAM application...")
    run_command(package_command)

    deploy_command = (
        "sam deploy "
        "--template-file gen/template-generated.yaml "
        f"--stack-name {env_variables.get('stack_name')} "
        "--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM "
        f"--parameter-overrides Stage={env_variables.get('stage_name')}"
    )
    logger.info("Deploying SAM application...")
    run_command(deploy_command)


def main():
    deploy_stack(**cognito_stack, action="update")
    deploy_stack(**iam_stack, action="update")
    deploy_stack(**static_content_bucket_stack, action="update")
    deploy_stack(**dynamodb_stack, action="update")
    apigateway_lambda_deploy_sam()


if __name__ == "__main__":
    main()
