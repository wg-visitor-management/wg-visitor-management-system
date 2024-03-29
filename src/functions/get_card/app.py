"""
This module is used to get all the cards from the database.
"""

import os

from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.config.config import CARD_STATUS
from vms_layer.helpers.response_parser import ParseResponse, remove_keys
APP_NAME = os.getenv("ApplicationName")

logger = get_logger(APP_NAME)
db_helper = DBHelper()


@handle_errors
@rbac
def lambda_handler(event, context):
    """
    This function is used to get all the cards from the database.
    """
    logger.debug(f"Received event: {event}")
    logger.debug(f"Received context: {context}")
    data = db_helper.query_items(
        key_condition_expression="PK = :pk AND begins_with(SK, :sk)",
        expression_attribute_values={":pk": "card", ":sk": "card#"},
        page_size=1000
    ).get("Items")
    if data:
        cards = parse_cards_data(data)
        return ParseResponse(cards, 200).return_response()
    return ParseResponse([], 200).return_response()


def parse_cards_data(cards):
    """
    This function is used to parse the cards data."""
    cards_data = []
    for card in cards:
        if card.get("cardStatus") != CARD_STATUS.get("DISCARDED"):
            card['card_id'] = card.get('SK').split("#")[-1]
            card = remove_keys(card, ["PK", "SK"])
            cards_data.append(card)
    return cards_data
