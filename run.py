import subprocess
import boto3
import logging
import sam_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client_cf = boto3.client("cloudformation")

configurations = {
    "BucketName": "vms-static-content",
    "UserPoolName": "vms-user-pool",
    "UserPoolClientName": "vms-user-pool-client",
    "TableName": "vms-database",
    "RoleName": "vms-lambda-role-common",
}


outputs = {}

env_variables = {
    "ENVIRONMENT": sam_config.ENVIRONMENT,
    "sam_stack_name": "api-gateway-lambda-sam",
    "s3_bucket": sam_config.BUCKET_NAME,
}

static_content_bucket_stack = {
    "stack_name": "static-content-bucket-stack",
    "template_body_url": "cfn/static_content_bucket.yaml",
    "parameters": [
        {"ParameterKey": "BucketName", "ParameterValue": configurations.get("BucketName")},
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
cognito_stack = {
    "stack_name": "cognito-stack",
    "template_body_url": "cfn/cognito.yaml",
    "parameters": [
        {"ParameterKey": "Environment", "ParameterValue": env_variables.get("ENVIRONMENT")},
        {"ParameterKey": "UserPoolName", "ParameterValue": configurations.get("UserPoolName")},
        {
            "ParameterKey": "UserPoolClientName",
            "ParameterValue": configurations.get("UserPoolClientName"),
        },
    ],
    "capabilities": ["CAPABILITY_IAM"],
}
dynamodb_stack = {
    "stack_name": "dynamodb-stack",
    "template_body_url": "cfn/dynamodb.yaml",
    "parameters": [
        {"ParameterKey": "Environment", "ParameterValue": env_variables.get("ENVIRONMENT")},
        {"ParameterKey": "TableName", "ParameterValue": configurations.get("TableName")},
    ],
    "capabilities": ["CAPABILITY_IAM"],
}

iam_stack = {
    "stack_name": "iam-stack",
    "template_body_url": "cfn/iam_policy.yaml",
    "parameters": [
        {"ParameterKey": "Environment", "ParameterValue": env_variables.get("ENVIRONMENT")},
        {"ParameterKey": "RoleName", "ParameterValue": configurations.get("RoleName")},
        {"ParameterKey": "BucketArn", "ParameterValue": f"{outputs.get('BucketArn')}"},
        {"ParameterKey": "DynamoDBTableArn", "ParameterValue": f"{outputs.get('DynamoDBTableArn')}"},
    ],
    "capabilities": ["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
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
        f"--stack-name {env_variables.get('sam_stack_name')} "
        "--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM "
        f"--parameter-overrides Environment={env_variables.get('ENVIRONMENT')} "
        f"BucketName={outputs.get('BucketName')} "
        f"DynamoDBTable={outputs.get('DynamoDBTableName')} "
        f"UserPoolId={outputs.get('UserPoolId')} "
        f"UserPoolClientId={outputs.get('UserPoolClientId')} "
        f"LambdaIAMRoleArn={outputs.get('LambdaIAMRoleArn')} "
        f"CognitoPoolArn={outputs.get('CognitoPoolArn')} "

    )
    logger.info("Deploying SAM application...")
    run_command(deploy_command)


def main():
    deploy_stack(**static_content_bucket_stack)
    deploy_stack(**cognito_stack)
    deploy_stack(**dynamodb_stack)
    deploy_stack(**iam_stack)
    apigateway_lambda_deploy_sam()


if __name__ == "__main__":
    main()
