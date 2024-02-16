"""This module updates a card with a visit_id and status."""
import json
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.config.schemas.card_schema import card_update_schema

logger = get_logger("POST /card/:id")
db_helper = DBHelper()


@handle_errors
@rbac
@validate_schema(card_update_schema)
def lambda_handler(event, context):
    """
    Update a card with a visit_id and status
    """
    body = json.loads(event.get("body"))
    logger.debug("Received event: %s", event)
    logger.debug("Received context: %s", context)

    card_id = event.get("pathParameters").get("id")
    visit_id = body.get("visitId")
    card_status = body.get("status")

    logger.info("Updating card %s with visit_id %s and status %s", card_id, visit_id, card_status)

    response = db_helper.get_item(
        key={"PK": "card", "SK": f"card#{card_id}"}
    )
    if not response:
        logger.error("Card not found")
        return ParseResponse({"message": "Card not found"}, 404).return_response()
    if response.get("cardStatus") == "occupied" and response.get("cardStatus") == "discarded":
        logger.error("Card is already occupied. Cannot be discarded.")
        return ParseResponse(
            {"message": "Card is already occupied. Cannot be discarded."},
            400).return_response()
    response = db_helper.update_item(
        key={"PK": "card", "SK": f"card#{card_id}"},
        update_expression="SET visit_id = :visit_id, cardStatus = :cardStatus",
        expression_attribute_values={
            ":visit_id": visit_id,
            ":cardStatus": card_status,
        },
    )
    logger.debug("Response from update_item: %s", response)
    logger.info("Card updated successfully")
    return ParseResponse(
        {"message": "Card updated successfully", "response": response},
        200,
    ).return_response()
