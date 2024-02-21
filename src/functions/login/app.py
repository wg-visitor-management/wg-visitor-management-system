"""
This module contains the code for the login lambda function.
"""
import os
import json
import boto3

from vms_layer.utils.loggers import get_logger
from vms_layer.config.schemas.login_schema import login_schema
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.custom_errors import NotAuthorizedException, UserNotFoundException
from vms_layer.helpers.response_parser import ParseResponse

CLIENT_ID = os.getenv("UserPoolClientId")
APP_NAME = os.getenv("ApplicationName")

client = boto3.client("cognito-idp")
logger = get_logger(APP_NAME)


@handle_errors
@validate_schema(login_schema)
def lambda_handler(event, context):
    """
    This function is used to authenticate a user.
    """
    logger.debug("Received event: %s", event)
    logger.debug("Received context: %s", context)
    body = json.loads(event.get("body"))
    email = body.get("username")
    password = body.get("password")

    try:
        response = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
            ClientId=CLIENT_ID,
        )
        return ParseResponse(
            response.get("AuthenticationResult"), 200
        ).return_response()

    except client.exceptions.NotAuthorizedException as exc:
        logger.error("Incorrect username or password")
        raise NotAuthorizedException("Incorrect username or password") from exc
    except client.exceptions.UserNotFoundException as exc:
        logger.error("User does not exist")
        raise UserNotFoundException("User does not exist") from exc
