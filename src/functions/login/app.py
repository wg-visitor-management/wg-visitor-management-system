import json
import boto3
import os
from vms_layer.helpers.response_parser import ParseResponse


def lambda_handler(event, context):
    client = boto3.client("cognito-idp")
    body = json.loads(event.get("body"))
    email = body.get("username")
    password = body.get("password")
    client_id = os.environ.get("UserPoolClientId")

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
        return ParseResponse("Incorrect username or password", 401).return_response()
    except client.exceptions.UserNotFoundException:
        return ParseResponse("User does not exist", 404).return_response()
    except Exception as e:
        return ParseResponse(str(e), 500).return_response()
