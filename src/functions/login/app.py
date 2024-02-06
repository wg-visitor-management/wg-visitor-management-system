import json
import boto3
import os

from vms_layer.config.schemas.login_schema import login_schema
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.custom_errors import NotAuthorizedException, UserNotFoundException
from vms_layer.helpers.response_parser import ParseResponse
client = boto3.client("cognito-idp")
client_id = os.getenv("UserPoolClientId")

@handle_errors
@validate_schema(login_schema)
def lambda_handler(event, context):
    body = json.loads(event.get("body"))
    email = body.get("username")
    password = body.get("password")

    try:
        response = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
            ClientId=client_id,
        )
        return ParseResponse(
            response.get("AuthenticationResult"), 200
        ).return_response()

    except client.exceptions.NotAuthorizedException:
        raise NotAuthorizedException("Incorrect username or password")
    except client.exceptions.UserNotFoundException:
        raise UserNotFoundException("User does not exist")
