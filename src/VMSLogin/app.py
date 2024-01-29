import json
import boto3
import os


def lambda_handler(event, context):
    client = boto3.client("cognito-idp")
    body = json.loads(event.get("body"))
    email = body.get("userName")
    password = body.get("password")
    client_id = os.environ.get("UserPoolClientId")

    try:
        response = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
            ClientId=client_id,
        )
        return {
            "statusCode": 200,
            "body": json.dumps(response.get("AuthenticationResult")),
        }
    except client.exceptions.NotAuthorizedException:
        return {"statusCode": 401, "body": json.dumps({"error": "Unauthorized"})}
    except client.exceptions.UserNotFoundException:
        return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
