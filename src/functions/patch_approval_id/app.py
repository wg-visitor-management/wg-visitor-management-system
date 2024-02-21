"""
PATCH /approval/:id
This module contains the code for the patch_approval_id lambda function.
"""

import os
import json

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

APP_NAME = os.getenv("ApplicationName")

logger = get_logger(APP_NAME)
db_helper = DBHelper()


def update_partition(update_partition_data):
    """
    Update the approval status for the visit and history partition
    """
    partition = update_partition_data.get("partition")
    quarter = update_partition_data.get("quarter")
    timestamp = update_partition_data.get("timestamp")
    visitor_id = update_partition_data.get("visitor_id")
    status = update_partition_data.get("status")
    approved_by = update_partition_data.get("approved_by")
    current_time = update_partition_data.get("current_time")

    history_key = {
        "PK": f"{partition}#{quarter}",
        "SK": f"{partition}#{timestamp}#{visitor_id}",
    }
    visit_key = {
        "PK": f"{partition}#{quarter}",
        "SK": f"{partition}#{visitor_id}#{timestamp}",
    }
    logger.debug(
        "Updating %s with key %s and status %s", partition, history_key, status
    )
    if partition == "visit":
        key = visit_key
    else:
        key = history_key
    query = "SET approvalStatus = :status, approvedBy = :approvedBy, approvalTime = :approvalTime"
    response = db_helper.update_item(
        key=key,
        update_expression=query,
        expression_attribute_values={
            ":status": status,
            ":approvedBy": approved_by,
            ":approvalTime": current_time,
        },
    )
    return response


@handle_errors
@rbac
@validate_schema(patch_approval_schema)
def lambda_handler(event, context):
    """
    This function is the entry point for
    the patch_approval_id lambda function.
    """
    visit_id = event.get("pathParameters").get("id")
    logger.debug("Received context: %s", context)
    logger.debug("Received event: %s", event)
    update_partition_data = get_update_partition_data(visit_id, event)
    if update_partition_data.get("status") in ("approved", "rejected"):
        update_partition(update_partition_data)
        update_partition_data["partition"] = "history"
        update_partition(update_partition_data)
        logger.info("Approval status updated successfully")

    return ParseResponse(
        {
            "message": "Approval status updated successfully",
            "visitId": visit_id,
            "approvedBy": update_partition_data.get("approved_by"),
            "status": update_partition_data.get("status"),
        },
        200,
    ).return_response()


def get_update_partition_data(visit_id, event):
    """
    Get the data to update the partition
    """
    body = json.loads(event.get("body"))
    decoded_visit_id = base64_to_string(visit_id)
    status = body.get("status")
    visitor_id = decoded_visit_id.split("#")[0]
    timestamp = decoded_visit_id.split("#")[1]
    quarter = extract_quarters_from_date_range(
        epoch_to_date(int(timestamp)), epoch_to_date(int(timestamp))
    )[0]
    authorizer = event.get("requestContext").get("authorizer")
    approved_by = authorizer.get("claims").get("name")
    current_time = str(current_time_epoch())
    logger.info(
        "Updating approval status for visit %s with status %s", visit_id, status
    )

    return {
        "partition": "visit",
        "quarter": quarter,
        "timestamp": timestamp,
        "visitor_id": visitor_id,
        "status": status,
        "approved_by": approved_by,
        "current_time": current_time,
    }
