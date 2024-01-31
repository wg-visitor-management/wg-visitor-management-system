import json
import os
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.config.schemas.card_schema import card_schema
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.config.config import CARD_STATUS
from vms_layer.utils.custom_errors import CardAlreadyExistsError

db_helper = DBHelper(os.environ["DynamoDBTableName"])
logger = get_logger("POST_/card")


@validate_schema(schema=card_schema)
@rbac
@handle_errors
def lambda_handler(event, context):
    logger.debug(event)

    request_body = json.loads(event["body"])
    card_id = request_body.get('card_id')

    check_if_card_exists(card_id)

    body = {}
    body["PK"] = "card"
    body["SK"] = f"card#{card_id}"
    body["status"] = CARD_STATUS.get("AVAILABLE")
    db_helper.create_item(body)

    resposne_body = {
        "card_id" : request_body.get("card_id"),
        "status" : CARD_STATUS.get("AVAILABLE")
    }
    return ParseResponse(resposne_body, 201).return_response()


def check_if_card_exists(card_id):
    card = db_helper.get_item({"PK": "card", "SK": f"card#{card_id}"})
    if card:
        raise CardAlreadyExistsError("Card With This Id Already Exists")
    return False