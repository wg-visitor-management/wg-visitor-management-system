import json
import os
import boto3

from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.config.schemas.password_schema import password_schema

client = boto3.client('cognito-idp')

logger = get_logger("POST /forgot-password")
client_id = os.getenv("UserPoolClientId")

def get_token(alias):
    client.forgot_password(
    ClientId=client_id,
    Username=alias,
    )

def change_password(alias, code, password):
    client.confirm_forgot_password(
    ClientId=client_id,
    Username=alias,
    ConfirmationCode=code,
    Password=password,
    )

@handle_errors
@validate_schema(password_schema)
def lambda_handler(event, context):  
    body = json.loads(event.get('body'))
    logger.debug(f"Received event: {event}")
    action = body.get('action')
    message = ""

    if action == 'get_token':
        logger.debug(f"Getting token for {body.get('alias')}")
        alias = body.get('alias')
        get_token(alias)
        logger.info(f"Token sent successfully")
        message = "Password reset link sent successfully"

    elif action == 'change_password':
        logger.debug(f"Changing password for {body.get('alias')}")
        alias = body.get('alias')
        code = body.get('code')
        password = body.get('password')
        change_password(alias, code, password) 
        logger.info(f"Password changed successfully")
        message = "Password changed successfully" 

    return ParseResponse({
        'message': message
    }, 200).return_response()
    