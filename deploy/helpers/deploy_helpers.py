import logging
import subprocess
import boto3

from helpers.run_helper import get_stack_qualifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client_cf = boto3.client("cloudformation")


outputs = {}


def get_outputs():
    return outputs


def extract_outputs(response):
    for output in response["Stacks"][0]["Outputs"]:
        outputs[output["OutputKey"]] = output["OutputValue"]


def get_stack_outputs(stack_name):
    try:
        response = client_cf.describe_stacks(StackName=stack_name)
        extract_outputs(response)
    except Exception as error:
        logger.info(f"Couldn't describe stack: {stack_name}")
        return False
    else:
        logger.info(f"Stack: {stack_name} exists!\n")
        return True


def deploy_stack(stack_name, template_body_url, parameters, capabilities):
    logger.debug(f"Deploying stack: {stack_name} with parameters: {parameters}")
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
        return outputs


def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
