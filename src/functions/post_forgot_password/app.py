"""This module is the entry point for the lambda function."""

import os
import json
import boto3

from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.config.schemas.password_schema import password_schema

APP_NAME = os.getenv("ApplicationName")

logger = get_logger(APP_NAME)
client = boto3.client("cognito-idp")
CLIENT_ID = os.getenv("UserPoolClientId")

def get_token(alias):
    """Send a token to the user's email."""
    try:
        client.forgot_password(
            ClientId=CLIENT_ID,
            Username=alias,
        )
    except client.exceptions.UserNotFoundException as exc:
        raise ValueError("User not found.") from exc
    except Exception as exc:
        raise ValueError("Cannot send token.") from exc


def change_password(alias, code, password):
    """Change the user's password."""
    try:
        client.confirm_forgot_password(
            ClientId=CLIENT_ID,
            Username=alias,
            ConfirmationCode=code,
            Password=password,
        )
    except client.exceptions.CodeMismatchException as exc:
        raise ValueError("Invalid OTP, Please Try Again.") from exc
    except client.exceptions.ExpiredCodeException as exc:
        raise ValueError("OTP expired. Please request a new one.") from exc
    except client.exceptions.UserNotFoundException as exc:
        raise ValueError("User not found.") from exc
    except Exception as exc:
        raise ValueError("Cannot change password.") from exc


@handle_errors
@validate_schema(password_schema)
def lambda_handler(event, context):
    """This function is used to send an email to the approver"""
    body = json.loads(event.get("body"))
    logger.debug("Received event: %s", event)
    logger.debug("Received context: %s", context)
    action = body.get("action")
    message = ""

    if action == "get_token":
        logger.debug("Getting token for %s", body.get("alias"))
        alias = body.get("alias")
        get_token(alias)
        logger.info("Token sent successfully")
        message = "Password reset link sent successfully"

    elif action == "change_password":
        logger.debug("Changing password for %s", body.get("alias"))
        alias = body.get("alias")
        code = body.get("code")
        password = body.get("password")
        change_password(alias, code, password)
        logger.info("Password changed successfully")
        message = "Password changed successfully"

    return ParseResponse({"message": message}, 200).return_response()
