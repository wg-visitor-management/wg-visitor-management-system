import json
import os
from helpers.body_parser import Visit
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.utils.base64_parser import convert_to_base64
from vms_layer.utils.base64_parser import base64_to_string
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.date_time_parser import (
    extract_quarters_from_date_range,
    epoch_to_date,
    current_time_epoch,
)
from vms_layer.config.schemas.visit_schema import post_visit_schema

db_helper = DBHelper(os.getenv("DynamoDBTableName"))
logger = get_logger("POST /visit")


@handle_errors
@rbac
@validate_schema(post_visit_schema)
def lambda_handler(event, context):
    body = json.loads(event.get("body"))
    logger.debug(f"Received event: {event}")
    current_time = current_time_epoch()
    current_date = epoch_to_date(current_time)
    current_quarter = extract_quarters_from_date_range(current_date, current_date)[0]
    visitor_id = base64_to_string(body.get("visitor_id"))
    checked_in_by = (
        event.get("requestContext").get("authorizer").get("claims").get("name")
    )

    visit = Visit(body, current_quarter, visitor_id, current_time, checked_in_by)
    item_data = visit.to_object()

    logger.info(f"Creating visit for visitor {visitor_id} with data: {item_data}")
    create_item_in_database(item_data, current_quarter, current_time, visitor_id)
    logger.info(f"Visit created successfully")

    response_data = {
        "message": "Visit created successfully",
        "visitor_id": body.get("visitor_id"),
        "checked_in_by": checked_in_by,
        "check_in_time": epoch_to_date(current_time),
        "visitId": convert_to_base64(f"{visitor_id}#{current_time}") + "==",
    }

    return ParseResponse(response_data, 200).return_response()


def create_item_in_database(item_data, current_quarter, current_time, visitor_id):
    db_helper.create_item(item_data)
    item_data.pop("PK")
    item_data.pop("SK")

    history_item_data = {
        "PK": f"history#{current_quarter}",
        "SK": f"history#{current_time}#{visitor_id}",
        **item_data,
    }
    logger.debug(f"Creating history item with data: {history_item_data}")
    db_helper.create_item(history_item_data)
