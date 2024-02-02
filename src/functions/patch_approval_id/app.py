import json
import os
import time
import base64
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.utils.loggers import get_logger
from vms_layer.utils.base64_parser import base64_to_string

from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.date_time_parser import (
    extract_quarters_from_date_range,
    epoch_to_date,
    current_time_epoch,
)
from vms_layer.config.schemas.approval_schema import patch_approval_schema

logger = get_logger("PATCH /approval/:id")
db_helper = DBHelper(os.environ.get("DynamoDBTableName"))

def update_partition(
    db_helper,
    partition,
    quarter,
    timestamp,
    visitor_id,
    status,
    approved_by,
    current_time,
):
    history_key = {
        "PK": f"{partition}#{quarter}",
        "SK": f"{partition}#{timestamp}#{visitor_id}",
    }
    visit_key = {
        "PK": f"{partition}#{quarter}",
        "SK": f"{partition}#{visitor_id}#{timestamp}",
    }
    logger.debug(f"Updating {partition} with key {history_key} and status {status}")
    if partition == "visit":
        key = visit_key
    else:
        key = history_key
    response = db_helper.update_item(
        key=key,
        update_expression="SET approval_status = :status, approved_by = :approved_by, approval_time = :approval_time",
        expression_attribute_values={
            ":status": status,
            ":approved_by": approved_by,
            ":approval_time": current_time,
        },
    )
    return response


@handle_errors
@rbac
@validate_schema(patch_approval_schema)
def lambda_handler(event, context):
    visit_id = event.get("pathParameters").get("id")
    body = json.loads(event.get("body"))
    logger.debug(f"Received event: {event}")
    decoded_visit_id = base64_to_string(visit_id)
    status = body.get("status")
    visitor_id = decoded_visit_id.split("#")[0]
    timestamp = decoded_visit_id.split("#")[1]
    quarter = extract_quarters_from_date_range(
        epoch_to_date(int(timestamp)), epoch_to_date(int(timestamp))
    )[0]
    approved_by = (
        event.get("requestContext").get("authorizer").get("claims").get("name")
    )
    current_time = str(current_time_epoch())
    
    logger.info(
        f"Updating approval status for visit {visit_id} with status {status} and approved by {approved_by}"
    )
    if status in ("approved", "rejected"):
        update_partition(
            db_helper,
            "visit",
            quarter,
            timestamp,
            visitor_id,
            status,
            approved_by,
            current_time,
        )
        update_partition(
            db_helper,
            "history",
            quarter,
            timestamp,
            visitor_id,
            status,
            approved_by,
            current_time,
        )
        logger.info(f"Approval status updated successfully")

    return ParseResponse(
        {
            "message": "Approval status updated successfully",
            "visit_id": visit_id,
            "approved_by": approved_by,
            "status": status,
        },
        200,
    ).return_response()
