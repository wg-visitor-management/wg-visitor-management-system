"""
This module is used to approve or reject a visit request. 
It updates the visit and history tables with the approval status 
and the admin who approved the request.
"""

import os
import jwt

from vms_layer.utils.loggers import get_logger
from vms_layer.utils.base64_parser import base64_to_string
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.date_time_parser import (
    extract_quarters_from_date_range,
    epoch_to_date,
    current_time_epoch,
)

logger = get_logger("GET /approval")
db_helper = DBHelper()


def update_partition(update_partition_data):
    """
    This function is used to update the visit and history tables with the approval status
    and the admin who approved the request.
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

    query = "SET approvalStatus = :status, approvedBy = :approvedBy, approvalTime = :approvalTime"
    if partition == "visit":
        key = visit_key
    else:
        key = history_key
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


def lambda_handler(event, context):
    """This function is used to approve or reject a visit request"""
    visit_id = event.get("pathParameters").get("id")
    access_token = event.get("queryStringParameters").get("access_token")
    action = event.get("queryStringParameters").get("action")
    token = jwt.decode(access_token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    name = token.get("name")
    logger.debug("Received event: %s", event)
    logger.debug("Received context: %s", context)
    decoded_visit_id = base64_to_string(visit_id)
    visitor_id = decoded_visit_id.split("#")[0]
    timestamp = decoded_visit_id.split("#")[1]
    quarter = extract_quarters_from_date_range(
        epoch_to_date(int(timestamp)), epoch_to_date(int(timestamp))
    )[0]
    current_time = str(current_time_epoch())
    approved_by = "admin"
    update_partition_data = {
        "visit": {
            "partition": "visit",
            "quarter": quarter,
            "timestamp": timestamp,
            "visitor_id": visitor_id,
            "status": action,
            "approved_by": approved_by,
            "current_time": current_time,
        },
        "history": {
            "partition": "history",
            "quarter": quarter,
            "timestamp": timestamp,
            "visitor_id": visitor_id,
            "status": action,
            "approved_by": approved_by,
            "current_time": current_time,
        },
    }

    if action in ("approved", "rejected"):
        update_partition(update_partition_data.get("visit"))
        update_partition(update_partition_data.get("history"))
    logger.debug("Returning response")
    return ParseResponse({"name": name, "visitId": visit_id}, 200).return_response()
