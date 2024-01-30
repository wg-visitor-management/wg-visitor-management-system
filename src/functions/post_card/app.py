import json
import os
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.config.schemas.card_schema import card_schema
from vms_layer.helpers.db_helper import DBHelper


@rbac
@validate_schema(schema=card_schema)
def lambda_handler(event, context):
    request_body = json.loads(event["body"])
    db_helper = DBHelper(os.environ["DynamoDBTableName"])
    body = {}
    body["PK"] = "card"
    body["SK"] = f"card#{request_body['card_id']}"
    body["status"] = "inactive"
    db_helper.create_item(body)
    return {"statusCode": 200, "body": json.dumps({"success": True})}
