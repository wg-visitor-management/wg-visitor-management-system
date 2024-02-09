"""
This module contains the code for the get_card_id lambda function.
"""
import os

from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.utils.custom_errors import InvalidCardIdError

db_helper = DBHelper()
logger = get_logger("POST_/card")


@handle_errors
@rbac
def lambda_handler(event, context):
    """
    This function is used to get a card from the database.
    """
    card_id = event.get('pathParameters').get('id')
    logger.debug("Received event: %s", event)
    logger.debug("Received context: %s", context)

    data = db_helper.get_item({"PK": "card", "SK": f"card#{card_id}"})
    if data:
        data.pop("PK")
        data['card_id'] = data.get('SK').split("#")[-1]
        data.pop("SK")
        logger.debug("Card Data: %s", data)
        return ParseResponse(data, 200).return_response()
    logger.error("Invalid Card Id Provided")
    raise InvalidCardIdError("Invalid Card Id Provided")
