"""This module is used to create a card."""
import os
import json

from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.config.schemas.card_schema import card_schema
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.config.config import CARD_STATUS
from vms_layer.utils.custom_errors import CardAlreadyExistsError

APP_NAME = os.getenv("ApplicationName")

logger = get_logger(APP_NAME)
db_helper = DBHelper()

@handle_errors
@validate_schema(schema=card_schema)
@rbac
def lambda_handler(event, context):
    """
    This function is used to create a card
    """
    logger.debug(f"Received event: {event}")
    logger.debug(f"Received context: {context}")
    cards = json.loads(event.get("body"))
    logger.debug(f"Creating cards {cards}")
    for card_id in cards:
        check_if_card_exists(card_id)
        body = {}
        body["PK"] = "card"
        body["SK"] = f"card#{card_id}"
        body["cardStatus"] = CARD_STATUS.get("AVAILABLE")
        db_helper.create_item(body)

    response = []
    for card_id in cards:
        response.append(
            {"card_id": card_id, "cardStatus": CARD_STATUS.get("AVAILABLE")}
        )
    logger.info("Card created successfully")
    return ParseResponse(response, 201).return_response()


def check_if_card_exists(card_id):
    """
    This function is used to check if the card already exists
    """
    logger.info("Checking if card exists")
    card = db_helper.get_item({"PK": "card", "SK": f"card#{card_id}"})
    if card:
        if card.get("cardStatus") == "discarded":
            logger.error(f"Card With {card_id} is already discarded")
            return False
        raise CardAlreadyExistsError(f"Card With {card_id} Id Already Exists")
    return False
