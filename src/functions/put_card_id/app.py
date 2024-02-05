import json
import os
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.config.schemas.card_schema import card_update_schema

logger = get_logger("POST /card/:id")
db_helper = DBHelper(os.getenv("DynamoDBTableName"))


@handle_errors
@rbac
@validate_schema(card_update_schema)
def lambda_handler(event, context):
    body = json.loads(event.get("body"))
    logger.debug(f"Received event: {event}")
    card_id = event.get("pathParameters").get("id")
    visit_id = body.get("visitId")
    cardStatus = body.get("status")

    logger.info(
        f"Updating card {card_id} with visit_id {visit_id} and status {cardStatus}"
    )
    response = db_helper.update_item(
        key={"PK": "card", "SK": f"card#{card_id}"},
        update_expression="SET visit_id = :visit_id, cardStatus = :cardStatus",
        expression_attribute_values={
            ":visit_id": visit_id,
            ":cardStatus": cardStatus,
        },
    )
    logger.debug(f"Response from db: {response}")
    logger.info("Card updated successfully")
    return ParseResponse(
        {"message": "Card updated successfully", "response": response},
        200,
    ).return_response()
