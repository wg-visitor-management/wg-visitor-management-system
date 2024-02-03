import json
import os
from vms_layer.utils.loggers import get_logger 
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.utils.base64_parser import base64_to_string
from vms_layer.utils.date_time_parser import date_to_epoch, epoch_to_date, extract_quarters_from_date_range

from vms_layer.utils.handle_errors import handle_errors

db_helper = DBHelper(os.getenv("DynamoDBTableName"))
logger = get_logger("GET /visit/:id")

@handle_errors
@rbac
def lambda_handler(event, context):
    path_params = event.get("pathParameters")
    logger.debug(f"Received event: {event}")
    visit_id = path_params.get("id")
    decoded_visit_id = base64_to_string(visit_id)
    visitor_id = decoded_visit_id.split("#")[0]
    visit_time = decoded_visit_id.split("#")[1]
    quarter = extract_quarters_from_date_range(epoch_to_date(int(visit_time)), epoch_to_date(int(visit_time)))[0]

    response = db_helper.get_item(
        key={
            "PK": f"visit#{quarter}",
            "SK": f"visit#{visitor_id}#{visit_time}",
        }
    )
    logger.debug(f"Response from db: {response}")
    response.pop("PK")
    response.pop("SK")
    response["date"] = epoch_to_date(int(response["check_in_time"])).split("T")[0]
    response["check_in_time"] = epoch_to_date(int(response["check_in_time"])).split("T")[1]
    logger.info(f"Visit {visit_id} retrieved successfully")

    return ParseResponse(response, 200).return_response()