import jwt
import os
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
db_helper = DBHelper(os.getenv("DynamoDBTableName"))



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


def lambda_handler(event, context):
    visit_id = event.get("pathParameters").get("id")
    access_token = event.get("queryStringParameters").get("access_token")
    action = event.get("queryStringParameters").get("action")
    token = jwt.decode(access_token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    name = token.get("name")
    logger.debug(f"Received event: {event}")
    decoded_visit_id = base64_to_string(visit_id)
    visitor_id = decoded_visit_id.split("#")[0]
    timestamp = decoded_visit_id.split("#")[1]
    quarter = extract_quarters_from_date_range(
        epoch_to_date(int(timestamp)), epoch_to_date(int(timestamp))
    )[0]
    current_time = str(current_time_epoch())
    approved_by = "admin"

    if action in ("approved", "rejected"):
        update_partition(
            db_helper,
            "visit",
            quarter,
            timestamp,
            visitor_id,
            action,
            approved_by,
            current_time,
        )
        update_partition(
            db_helper,
            "history",
            quarter,
            timestamp,
            visitor_id,
            action,
            approved_by,
            current_time,
        )
    return ParseResponse({"name": name, "visit_id": visit_id}, 200).return_response()
