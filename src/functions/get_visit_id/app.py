"""
This module is the entry point for the lambda function for get_visit_id.
"""
import os

from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.response_parser import ParseResponse, remove_keys
from vms_layer.utils.base64_parser import base64_to_string
from vms_layer.utils.date_time_parser import (
    epoch_to_date,
    extract_quarters_from_date_range,
)
from vms_layer.utils.handle_errors import handle_errors

APP_NAME = os.getenv("ApplicationName")

logger = get_logger(APP_NAME)
db_helper = DBHelper()

@handle_errors
@rbac
def lambda_handler(event, context):
    """
    This function is used to get a visit from the database.
    """
    path_params = event.get("pathParameters")
    logger.debug(f"Received event: {event}")
    logger.debug(f"Received context: {context}")
    visit_id = path_params.get("id")
    decoded_visit_id = base64_to_string(visit_id)
    visitor_id = decoded_visit_id.split("#")[0]
    visit_time = decoded_visit_id.split("#")[1]
    quarter = extract_quarters_from_date_range(
        epoch_to_date(int(visit_time)), epoch_to_date(int(visit_time))
    )[0]

    response = db_helper.get_item(
        key={
            "PK": f"visit#{quarter}",
            "SK": f"visit#{visitor_id}#{visit_time}",
        }
    )
    logger.debug(f"Response from db: {response}")
    response = remove_keys(response, ["PK", "SK"])
    response["date"] = epoch_to_date(int(response["checkInTime"])).split("T")[0]
    response["checkInTime"] = epoch_to_date(int(response["checkInTime"])).split("T")[1]
    logger.debug(f"Response after parsing: {response}")
    logger.info("Visit Data Fetched Successfully")

    return ParseResponse(response, 200).return_response()
